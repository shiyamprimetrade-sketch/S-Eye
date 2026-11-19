package online.slickk.seye;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public final class ObservationReport {
    private static final char[] HEX = "0123456789abcdef".toCharArray();

    private ObservationReport() {}

    public static String encode(byte[] bytes, String sourceKind, int width, int height, String label) {
        if (!("document".equals(sourceKind) || "sample".equals(sourceKind) || "camera_thumbnail".equals(sourceKind)))
            throw new IllegalArgumentException("Unknown source kind");
        if (!("Circle".equals(label) || "Triangle".equals(label) || "Quadrilateral".equals(label)
                || ShapeRecognizer.UNKNOWN.equals(label))) throw new IllegalArgumentException("Unknown label");
        return "{\"format\":\"seye-android-observation-v1\",\"schema_version\":1,"
                + "\"app_version\":\"0.3.0-preview\","
                + "\"source_kind\":\"" + sourceKind + "\",\"sha256\":\"" + sha256(bytes) + "\","
                + "\"source_bytes\":" + bytes.length + ",\"analyzed_size\":[" + width + "," + height + "],"
                + "\"label\":\"" + label + "\",\"accepted\":" + !ShapeRecognizer.UNKNOWN.equals(label) + "}\n";
    }

    private static String sha256(byte[] bytes) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
            char[] result = new char[digest.length * 2];
            for (int i = 0; i < digest.length; i++) {
                int value = digest[i] & 255;
                result[i * 2] = HEX[value >>> 4];
                result[i * 2 + 1] = HEX[value & 15];
            }
            return new String(result);
        } catch (NoSuchAlgorithmException error) {
            throw new IllegalStateException("SHA-256 is unavailable", error);
        }
    }
}
