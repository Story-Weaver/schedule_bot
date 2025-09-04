import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.File;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

class Model {
    int id;
    String date;
    int group;
    int num_pair;
    String name_pair;
    String cab_pair;

    @Override
    public String toString() {
        return String.format(
            "Model{id=%d, date='%s', group=%d, num_pair=%d, name_pair='%s', cab_pair='%s'}",
            id, date, group, num_pair, name_pair, cab_pair
        );
    }
}

public class ScheduleParser {

    public static void main(String[] args) throws IOException {
        File input = new File("site.txt");
        Document doc = Jsoup.parse(input, "UTF-8");
        DatabaseManager manager = new DatabaseManager(Config.DB_URL, Config.DB_USER, Config.DB_PASSWORD);

        List<Model> allModels = parseAllSchedules(doc);
        
        System.out.println("Найдено записей: " + allModels.size());

        try {
            manager.createTablePair();
            manager.createTableUser();
            int beforeCount = manager.getRecordCount();
            System.out.println("Записей в базе до обновления: " + beforeCount);
            manager.updateScheduleData(allModels);
            int afterCount = manager.getRecordCount();
            System.out.println("Записей в базе после обновления: " + afterCount);
            System.out.println("Обновление расписания завершено успешно!");
        } catch (SQLException e) {
            System.out.println("Ошибка при обновлении расписания:");
            e.printStackTrace();
        }
    }

    private static List<Model> parseAllSchedules(Document doc) {
        List<Model> allModels = new ArrayList<>();
        Elements groupHeaders = doc.select("h2");
        
        for (Element groupH2 : groupHeaders) {
            String text = groupH2.text();
            if (!text.startsWith("Группа - ")) continue;
            
            String groupNumber = text.replace("Группа - ", "").trim();
            Element h3 = nextTag(groupH2, "h3");
            Element table = nextTag(h3 != null ? h3 : groupH2, "table");
            
            if (table != null) {
                List<String> dayDates = extractDayDates(table);
                List<Model> groupModels = parseLessons(table, dayDates, groupNumber);
                allModels.addAll(groupModels);
            }
        }
        
        return allModels;
    }

    private static List<String> extractDayDates(Element table) {
        Elements header = table.select("tr").get(0).select("th[colspan]");
        List<String> dayDates = new ArrayList<>();
        for (Element th : header) {
            String text = th.text();
            String[] parts = text.split(",");
            if (parts.length >= 2) {
                dayDates.add(parts[1].trim());
            } else {
                dayDates.add("");
            }
        }
        return dayDates;
    }

    private static List<Model> parseLessons(Element table, List<String> dayDates, String groupNumber) {
        List<Model> models = new ArrayList<>();
        Elements rows = table.select("tr");
        
        for (int i = 2; i < rows.size(); i++) {
            Element row = rows.get(i);
            Element th = row.selectFirst("th");
            if (th == null) continue;
            
            String numberText = th.text().replaceAll("[^0-9]", "");
            if (numberText.isEmpty()) continue;
            int pairNumber = Integer.parseInt(numberText);

            Elements cols = row.select("td");
            for (int d = 0; d < dayDates.size(); d++) {
                int subjIndex = d * 2;
                int roomIndex = subjIndex + 1;
                
                if (roomIndex >= cols.size()) continue;

                String subj = cols.get(subjIndex).text().trim();
                String room = cols.get(roomIndex).text().trim();

                if (subj.isEmpty() && room.isEmpty()) continue;

                Model model = new Model();
                model.id = 0;
                model.date = dayDates.get(d);
                model.group = Integer.parseInt(groupNumber.replace("*", ""));
                model.num_pair = pairNumber;
                model.name_pair = subj;
                model.cab_pair = room;
                
                models.add(model);
            }
        }
        return models;
    }

    private static Element nextTag(Element start, String tag) {
        if (start == null) return null;
        Element cur = start.nextElementSibling();
        while (cur != null) {
            if (cur.tagName().equalsIgnoreCase(tag)) return cur;
            cur = cur.nextElementSibling();
        }
        return null;
    }
}