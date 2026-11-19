package online.slickk.seye;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Paint;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.widget.Toast;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
    private static final int PICK_IMAGE = 1, CAPTURE_IMAGE = 2, SAVE_REPORT = 3;
    private static final int MAX_BYTES = 12 * 1024 * 1024;
    private static final long MAX_PIXELS = 32_000_000L;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private TextView result;
    private ImageView preview;
    private Button pick, sample, capture, save;
    private String currentReport;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll = new ScrollView(this);
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        int padding = dp(24);
        page.setPadding(padding, padding, padding, padding);
        page.setBackgroundColor(0xfff3f6f3);
        scroll.addView(page);
        if (android.os.Build.VERSION.SDK_INT >= 30) {
            scroll.setOnApplyWindowInsetsListener((view, insets) -> {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
                return insets;
            });
        }
        TextView title = new TextView(this);
        title.setText("S-Eye");
        title.setTextSize(32);
        title.setTextColor(0xff163b30);
        page.addView(title);
        TextView guidance = new TextView(this);
        guidance.setText("Choose or capture one high-contrast circle, triangle, or quadrilateral.");
        guidance.setTextColor(0xff30473f);
        guidance.setTextSize(16);
        guidance.setPadding(0, dp(8), 0, dp(16));
        page.addView(guidance);
        pick = new Button(this);
        pick.setText("Choose image");
        pick.setOnClickListener(view -> chooseImage());
        page.addView(pick);
        capture = new Button(this);
        capture.setText("Take photo");
        capture.setOnClickListener(view -> launch(new Intent(MediaStore.ACTION_IMAGE_CAPTURE), CAPTURE_IMAGE,
                "No camera app is available."));
        page.addView(capture);
        sample = new Button(this);
        sample.setText("Try sample");
        sample.setOnClickListener(view -> {
            Bitmap image = Bitmap.createBitmap(180, 180, Bitmap.Config.ARGB_8888);
            Canvas canvas = new Canvas(image);
            canvas.drawColor(Color.WHITE);
            Paint ink = new Paint(Paint.ANTI_ALIAS_FLAG);
            ink.setStyle(Paint.Style.STROKE);
            ink.setStrokeWidth(7);
            ink.setColor(Color.BLACK);
            canvas.drawCircle(90, 90, 48, ink);
            analyze(() -> bitmapSource(image, "sample"));
        });
        page.addView(sample);
        save = new Button(this);
        save.setText("Save observation JSON");
        save.setEnabled(false);
        save.setOnClickListener(view -> {
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.setType("application/json");
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.putExtra(Intent.EXTRA_TITLE, "seye-observation.json");
            launch(intent, SAVE_REPORT, "No document provider is available.");
        });
        page.addView(save);
        result = new TextView(this);
        result.setAccessibilityLiveRegion(TextView.ACCESSIBILITY_LIVE_REGION_POLITE);
        result.setTextSize(22);
        result.setTextColor(0xff163b30);
        result.setPadding(0, dp(14), 0, dp(14));
        page.addView(result);
        preview = new ImageView(this);
        preview.setContentDescription("Selected image preview");
        preview.setScaleType(ImageView.ScaleType.FIT_CENTER);
        page.addView(preview, new LinearLayout.LayoutParams(-1, dp(256)));
        setContentView(scroll);
        if (state != null) {
            currentReport = state.getString("observation");
            result.setText(state.getString("result"));
            save.setEnabled(currentReport != null);
        }
    }

    private void chooseImage() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.setType("image/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.putExtra(Intent.EXTRA_LOCAL_ONLY, true);
        launch(intent, PICK_IMAGE, "No Android file picker is available.");
    }

    private void launch(Intent intent, int request, String message) {
        try {
            startActivityForResult(intent, request);
        } catch (android.content.ActivityNotFoundException | SecurityException error) {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
        }
    }

    @Override protected void onActivityResult(int request, int status, Intent data) {
        super.onActivityResult(request, status, data);
        if (status != RESULT_OK || data == null) return;
        Uri uri = data.getData();
        if (request == PICK_IMAGE && uri != null) {
            analyze(() -> readImage(uri));
        } else if (request == CAPTURE_IMAGE && data.getExtras() != null) {
            Object thumbnail = data.getExtras().get("data");
            if (thumbnail instanceof Bitmap) {
                analyze(() -> bitmapSource((Bitmap) thumbnail, "camera_thumbnail"));
            } else {
                Toast.makeText(this, "No camera thumbnail returned.", Toast.LENGTH_SHORT).show();
            }
        } else if (request == SAVE_REPORT && uri != null && currentReport != null) {
            writeReport(uri, currentReport);
        }
    }

    private static final class ImageInput {
        final Bitmap bitmap;
        final byte[] encoded;
        final String kind;

        ImageInput(Bitmap bitmap, byte[] encoded, String kind) {
            this.bitmap = bitmap;
            this.encoded = encoded;
            this.kind = kind;
        }
    }

    private interface ImageSource {
        ImageInput get() throws IOException;
    }

    private ImageInput bitmapSource(Bitmap bitmap, String kind) throws IOException {
        double scale = (double) ShapeRecognizer.MAX_SIDE / Math.max(bitmap.getWidth(), bitmap.getHeight());
        if (scale < 1) {
            bitmap = Bitmap.createScaledBitmap(bitmap, Math.max(1, (int) (bitmap.getWidth() * scale)),
                    Math.max(1, (int) (bitmap.getHeight() * scale)), true);
        }
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, buffer)) throw new IOException("PNG encoding failed");
        return new ImageInput(bitmap, buffer.toByteArray(), kind);
    }

    private void writeReport(Uri uri, String report) {
        worker.execute(() -> {
            String message;
            try (OutputStream stream = getContentResolver().openOutputStream(uri, "w")) {
                if (stream == null) throw new IOException("No document stream");
                stream.write(report.getBytes(StandardCharsets.UTF_8));
                message = "Observation saved";
            } catch (IOException | RuntimeException error) {
                message = "Could not save the observation";
            }
            String text = message;
            runOnUiThread(() -> {
                if (!isDestroyed()) Toast.makeText(this, text, Toast.LENGTH_SHORT).show();
            });
        });
    }

    private void analyze(ImageSource source) {
        pick.setEnabled(false);
        sample.setEnabled(false);
        capture.setEnabled(false);
        save.setEnabled(false);
        currentReport = null;
        preview.setImageDrawable(null);
        result.setText("Analyzing image…");
        worker.execute(() -> {
            try {
                ImageInput input = source.get();
                Bitmap bitmap = input.bitmap;
                int w = bitmap.getWidth(), h = bitmap.getHeight();
                int[] pixels = new int[w * h];
                bitmap.getPixels(pixels, 0, w, 0, 0, w, h);
                String label = ShapeRecognizer.classify(pixels, w, h);
                show(bitmap, label, ObservationReport.encode(input.encoded, input.kind, w, h, label));
            } catch (IOException | RuntimeException error) {
                show(null, "Could not read this image. Try a smaller JPEG or PNG.", null);
            }
        });
    }

    private void show(Bitmap bitmap, String message, String report) {
        runOnUiThread(() -> {
            if (isDestroyed()) return;
            preview.setImageBitmap(bitmap);
            result.setText(message);
            pick.setEnabled(true);
            sample.setEnabled(true);
            capture.setEnabled(true);
            currentReport = report;
            save.setEnabled(report != null);
        });
    }

    private ImageInput readImage(Uri uri) throws IOException {
        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inJustDecodeBounds = true;
        byte[] encoded;
        try (InputStream input = getContentResolver().openInputStream(uri);
             ByteArrayOutputStream buffer = new ByteArrayOutputStream()) {
            if (input == null) throw new IOException("No image data");
            byte[] block = new byte[8192];
            for (int read; (read = input.read(block)) != -1; ) {
                if (buffer.size() + read > MAX_BYTES) throw new IOException("Image exceeds size limit");
                buffer.write(block, 0, read);
            }
            encoded = buffer.toByteArray();
        }
        BitmapFactory.decodeByteArray(encoded, 0, encoded.length, options);
        if (options.outWidth <= 0 || options.outHeight <= 0
                || (long) options.outWidth * options.outHeight > MAX_PIXELS)
            throw new IOException("Invalid image dimensions");
        int largest = Math.max(options.outWidth, options.outHeight);
        options.inSampleSize = 1;
        while ((largest + options.inSampleSize - 1) / options.inSampleSize > ShapeRecognizer.MAX_SIDE)
            options.inSampleSize *= 2;
        options.inJustDecodeBounds = false;
        options.inPreferredConfig = Bitmap.Config.ARGB_8888;
        Bitmap bitmap = BitmapFactory.decodeByteArray(encoded, 0, encoded.length, options);
        if (bitmap == null || bitmap.getWidth() > ShapeRecognizer.MAX_SIDE
                || bitmap.getHeight() > ShapeRecognizer.MAX_SIDE)
            throw new IOException("Decoder failed or returned an oversized image");
        return new ImageInput(bitmap, encoded, "document");
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        state.putString("observation", currentReport);
        if (currentReport != null) state.putString("result", result.getText().toString());
    }

    @Override protected void onDestroy() {
        worker.shutdownNow();
        super.onDestroy();
    }
}
