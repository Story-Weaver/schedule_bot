// DatabaseManager.java
import java.sql.*;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DatabaseManager {
    private final String url;
    private final String user;
    private final String password;

    public DatabaseManager(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    public void createTablePair() throws SQLException {
        String sql = """
            CREATE TABLE IF NOT EXISTS schedule (
                id SERIAL PRIMARY KEY,
                date VARCHAR(10) NOT NULL,
                group_number INTEGER NOT NULL,
                pair_number INTEGER NOT NULL,
                pair_name VARCHAR(255),
                cabinet VARCHAR(50),
                UNIQUE(date, group_number, pair_number)
            );
            
            CREATE INDEX IF NOT EXISTS idx_schedule_date_group 
            ON schedule(date, group_number);
            """;
        
        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        }
    }

    public void createTableUser() throws SQLException {
        String sql = """
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            group_number INTEGER NOT NULL,
            tg_user_id BIGINT NOT NULL UNIQUE,
            time INTEGER,
            count INTEGER
            );

            CREATE INDEX IF NOT EXISTS idx_user_tg_user_id ON users(tg_user_id);
            """;
        
        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        }
    }

    public void updateScheduleData(List<Model> models) throws SQLException {
        if (models == null || models.isEmpty()) {
            return;
        }
        
        // Получаем все уникальные комбинации дата+группа
        Set<String> dateGroupCombinations = new HashSet<>();
        for (Model model : models) {
            String key = model.date + "|" + model.group;
            dateGroupCombinations.add(key);
        }
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            conn.setAutoCommit(false);
            
            try {
                // Удаляем существующие записи для каждой комбинации дата+группа
                deleteDateGroupCombinations(conn, dateGroupCombinations);
                
                // Вставляем новые записи
                insertModels(conn, models);
                
                conn.commit();
                System.out.println("Данные успешно обновлены. Обработано " + models.size() + " записей.");
            } catch (SQLException e) {
                conn.rollback();
                throw e;
            }
        }
    }

    private void deleteDateGroupCombinations(Connection conn, Set<String> dateGroupCombinations) throws SQLException {
        String sql = "DELETE FROM schedule WHERE date = ? AND group_number = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (String combination : dateGroupCombinations) {
                String[] parts = combination.split("\\|");
                if (parts.length != 2) continue;
                
                String date = parts[0];
                int group = Integer.parseInt(parts[1]);
                
                pstmt.setString(1, date);
                pstmt.setInt(2, group);
                pstmt.addBatch();
            }
            
            int[] deleteCounts = pstmt.executeBatch();
            System.out.println("Удалено записей для " + deleteCounts.length + " комбинаций дата+группа");
        }
    }

    private void insertModels(Connection conn, List<Model> models) throws SQLException {
        String sql = "INSERT INTO schedule (date, group_number, pair_number, pair_name, cabinet) VALUES (?, ?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (Model model : models) {
                pstmt.setString(1, model.date);
                pstmt.setInt(2, model.group);
                pstmt.setInt(3, model.num_pair);
                pstmt.setString(4, model.name_pair);
                pstmt.setString(5, model.cab_pair);
                pstmt.addBatch();
            }
            
            pstmt.executeBatch();
        }
    }

    public int getRecordCount() throws SQLException {
        String sql = "SELECT COUNT(*) FROM schedule";
        
        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            if (rs.next()) {
                return rs.getInt(1);
            }
            return 0;
        }
    }
}