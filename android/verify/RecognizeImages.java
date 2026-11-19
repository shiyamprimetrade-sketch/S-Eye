import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.nio.file.Files;
import online.slickk.seye.ObservationReport;
import online.slickk.seye.ShapeRecognizer;

public final class RecognizeImages {
    public static void main(String[] paths) throws Exception {
        for (String path : paths) {
            BufferedImage image = ImageIO.read(new File(path));
            int width = image.getWidth(), height = image.getHeight();
            String name = new File(path).getName();
            String label = ShapeRecognizer.classify(
                image.getRGB(0, 0, width, height, null, 0, width), width, height);
            String payload = ObservationReport.encode(Files.readAllBytes(new File(path).toPath()),
                    "document", width, height, label);
            System.out.print(name + "\t" + payload);
        }
    }
}
