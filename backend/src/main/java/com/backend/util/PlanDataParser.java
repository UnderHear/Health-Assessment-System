package com.backend.util;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.util.StringUtils;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Parse markdown-style test reports to structured plan data and weekly schedules.
 */
public class PlanDataParser {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private static final List<String> DAY_ORDER = Arrays.asList("mon", "tue", "wed", "thu", "fri", "sat", "sun");
    private static final Map<String, String> DAY_MAP;
    static {
        Map<String, String> map = new HashMap<>();
        map.put("周一", "mon");
        map.put("周二", "tue");
        map.put("周三", "wed");
        map.put("周四", "thu");
        map.put("周五", "fri");
        map.put("周六", "sat");
        map.put("周日", "sun");
        map.put("周天", "sun");
        DAY_MAP = Collections.unmodifiableMap(map);
    }

    public static String buildPlanData(String report, Integer totalWeeks) {
        if (!StringUtils.hasText(report)) {
            return null;
        }
        String planSection = extractPlanSection(report);
        if (!StringUtils.hasText(planSection)) {
            return null;
        }
        List<Phase> phases = parsePhases(planSection);
        if (phases.isEmpty()) {
            return null;
        }
        fillMissingWeekRanges(phases, totalWeeks);

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("phases", phases);
        try {
            return OBJECT_MAPPER.writeValueAsString(payload);
        } catch (Exception e) {
            return null;
        }
    }

    public static List<Map<String, Object>> buildWeeklySchedule(String planDataJson, int currentWeek) {
        if (!StringUtils.hasText(planDataJson)) {
            return Collections.emptyList();
        }
        try {
            Map<String, Object> planData = OBJECT_MAPPER.readValue(
                    planDataJson, new TypeReference<Map<String, Object>>() {});
            @SuppressWarnings("unchecked")
            List<LinkedHashMap<String, Object>> phases =
                    (List<LinkedHashMap<String, Object>>) planData.get("phases");
            if (phases == null || phases.isEmpty()) {
                return Collections.emptyList();
            }

            LinkedHashMap<String, Object> target = phases.get(0);
            for (LinkedHashMap<String, Object> ph : phases) {
                Integer start = toInt(ph.get("startWeek"));
                Integer end = toInt(ph.get("endWeek"));
                if (start != null && end != null && currentWeek >= start && currentWeek <= end) {
                    target = ph;
                    break;
                }
            }

            @SuppressWarnings("unchecked")
            List<LinkedHashMap<String, Object>> week =
                    (List<LinkedHashMap<String, Object>>) target.get("week");
            if (week == null) {
                return Collections.emptyList();
            }

            List<Map<String, Object>> ordered = new ArrayList<>();
            for (String dayKey : DAY_ORDER) {
                LinkedHashMap<String, Object> match = null;
                for (LinkedHashMap<String, Object> item : week) {
                    if (dayKey.equals(item.get("dayKey"))) {
                        match = item;
                        break;
                    }
                }
                if (match != null) {
                    ordered.add(match);
                } else {
                    Map<String, Object> empty = new HashMap<>();
                    empty.put("dayKey", dayKey);
                    empty.put("dayName", dayNameFromKey(dayKey));
                    empty.put("summary", "");
                    empty.put("detail", "");
                    ordered.add(empty);
                }
            }
            return ordered;
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private static String dayNameFromKey(String key) {
        switch (key) {
            case "mon": return "周一";
            case "tue": return "周二";
            case "wed": return "周三";
            case "thu": return "周四";
            case "fri": return "周五";
            case "sat": return "周六";
            case "sun": return "周日";
            default: return key;
        }
    }

    private static Integer toInt(Object value) {
        if (value instanceof Integer) return (Integer) value;
        if (value instanceof Number) return ((Number) value).intValue();
        if (value instanceof String) {
            try {
                return Integer.parseInt((String) value);
            } catch (NumberFormatException ignored) {
            }
        }
        return null;
    }

    private static String extractPlanSection(String report) {
        String normalized = report.replace("\r", "");
        int start = normalized.indexOf("分阶段训练计划");
        String after = start >= 0 ? normalized.substring(start) : normalized;

        int end = findFirstIndex(after,
                "运动禁忌", "五、", "5、", "六、", "6、", "### **五");
        if (end > 0) {
            return after.substring(0, end);
        }
        return after;
    }

    private static int findFirstIndex(String text, String... markers) {
        int min = -1;
        for (String marker : markers) {
            int idx = text.indexOf(marker);
            if (idx >= 0) {
                if (min == -1 || idx < min) {
                    min = idx;
                }
            }
        }
        return min;
    }

    private static List<Phase> parsePhases(String planSection) {
        String normalized = planSection.replace("\r", "");
        Pattern headerPattern = Pattern.compile("\\*\\*\\s*阶段[一二三四五六七八九十0-9]+[^\\n]*\\*\\*");
        Matcher matcher = headerPattern.matcher(normalized);
        List<int[]> ranges = new ArrayList<>();
        while (matcher.find()) {
            ranges.add(new int[]{matcher.start(), matcher.end()});
        }
        // Fallback: 没匹配到粗体标题时，使用非粗体“阶段X”作为分段
        if (ranges.isEmpty()) {
            Pattern fallbackHeader = Pattern.compile("阶段[一二三四五六七八九十0-9]+[^\\n]{0,50}");
            Matcher fm = fallbackHeader.matcher(normalized);
            while (fm.find()) {
                ranges.add(new int[]{fm.start(), fm.end()});
            }
        }
        List<Phase> phases = new ArrayList<>();
        for (int i = 0; i < ranges.size(); i++) {
            int start = ranges.get(i)[0];
            int end = (i + 1 < ranges.size()) ? ranges.get(i + 1)[0] : normalized.length();
            String header = normalized.substring(start, ranges.get(i)[1]);
            String content = normalized.substring(ranges.get(i)[1], end);

            Phase phase = new Phase();
            phase.setTitle(cleanMarkdown(header));

            populateWeeks(content, phase);
            populateGoalAndNotes(content, phase);
            parseWeekRange(phase);
            phases.add(phase);
        }
        return phases;
    }

    private static void populateGoalAndNotes(String content, Phase phase) {
        Matcher goal = Pattern.compile("阶段目标[:：]\\s*([^\\n]+)").matcher(content);
        if (goal.find()) {
            phase.setGoal(cleanMarkdown(goal.group(1)));
        }
        int notesIdx = content.indexOf("注意事项");
        if (notesIdx >= 0) {
            phase.setNotes(cleanMarkdown(content.substring(notesIdx)));
        }
    }

    private static void populateWeeks(String content, Phase phase) {
        Map<String, DayPlan> weekMap = new HashMap<>();
        // 逐行解析，匹配任意行内出现的“周X：内容”
        Pattern linePattern = Pattern.compile("周([一二三四五六日天])\\s*[:：]\\s*(.*)");
        for (String line : content.split("\n")) {
            Matcher lm = linePattern.matcher(line);
            if (lm.find()) {
                String dayName = "周" + lm.group(1);
                String dayKey = DAY_MAP.get(dayName);
                if (dayKey == null) continue;
                String text = cleanMarkdown(lm.group(2));
                DayPlan dp = new DayPlan();
                dp.setDayKey(dayKey);
                dp.setDayName(dayName);
                dp.setSummary(text);
                dp.setDetail(text);
                weekMap.put(dayKey, dp);
            }
        }
        List<DayPlan> week = new ArrayList<>();
        for (String key : DAY_ORDER) {
            if (weekMap.containsKey(key)) {
                week.add(weekMap.get(key));
            } else {
                DayPlan dp = new DayPlan();
                dp.setDayKey(key);
                dp.setDayName(dayNameFromKey(key));
                dp.setSummary("");
                dp.setDetail("");
                week.add(dp);
            }
        }
        phase.setWeek(week);
    }

    private static void parseWeekRange(Phase phase) {
        String title = phase.getTitle();
        Matcher range = Pattern.compile("第(\\d+)[-~—–－至到](\\d+)周").matcher(title);
        if (range.find()) {
            phase.setStartWeek(parseInt(range.group(1)));
            phase.setEndWeek(parseInt(range.group(2)));
            return;
        }
        Matcher single = Pattern.compile("第(\\d+)周").matcher(title);
        if (single.find()) {
            Integer w = parseInt(single.group(1));
            phase.setStartWeek(w);
            phase.setEndWeek(w);
        }
    }

    private static Integer parseInt(String text) {
        try {
            return Integer.parseInt(text);
        } catch (Exception e) {
            return null;
        }
    }

    private static void fillMissingWeekRanges(List<Phase> phases, Integer totalWeeks) {
        int weeks = (totalWeeks != null && totalWeeks > 0) ? totalWeeks : (phases.size() * 4);
        int cursor = 1;
        for (int i = 0; i < phases.size(); i++) {
            Phase phase = phases.get(i);
            if (phase.getStartWeek() == null) {
                phase.setStartWeek(cursor);
            }
            if (phase.getEndWeek() == null) {
                int remainingPhases = phases.size() - i;
                int evenLength = Math.max(1, (weeks - cursor + 1) / remainingPhases);
                int end = (i == phases.size() - 1) ? weeks : Math.min(weeks, cursor + evenLength - 1);
                phase.setEndWeek(end);
            }
            cursor = phase.getEndWeek() + 1;
        }
    }

    private static String cleanMarkdown(String text) {
        if (text == null) return "";
        return text.replace("**", "")
                .replace("*", "")
                .replace("`", "")
                .replaceAll("\\s+", " ")
                .trim();
    }

    public static class Phase {
        private String title;
        private Integer startWeek;
        private Integer endWeek;
        private List<DayPlan> week = new ArrayList<>();
        private String notes;
        private String goal;

        public String getTitle() {
            return title;
        }

        public void setTitle(String title) {
            this.title = title;
        }

        public Integer getStartWeek() {
            return startWeek;
        }

        public void setStartWeek(Integer startWeek) {
            this.startWeek = startWeek;
        }

        public Integer getEndWeek() {
            return endWeek;
        }

        public void setEndWeek(Integer endWeek) {
            this.endWeek = endWeek;
        }

        public List<DayPlan> getWeek() {
            return week;
        }

        public void setWeek(List<DayPlan> week) {
            this.week = week;
        }

        public String getNotes() {
            return notes;
        }

        public void setNotes(String notes) {
            this.notes = notes;
        }

        public String getGoal() {
            return goal;
        }

        public void setGoal(String goal) {
            this.goal = goal;
        }
    }

    public static class DayPlan {
        private String dayKey;
        private String dayName;
        private String summary;
        private String detail;

        public String getDayKey() {
            return dayKey;
        }

        public void setDayKey(String dayKey) {
            this.dayKey = dayKey;
        }

        public String getDayName() {
            return dayName;
        }

        public void setDayName(String dayName) {
            this.dayName = dayName;
        }

        public String getSummary() {
            return summary;
        }

        public void setSummary(String summary) {
            this.summary = summary;
        }

        public String getDetail() {
            return detail;
        }

        public void setDetail(String detail) {
            this.detail = detail;
        }
    }
}
