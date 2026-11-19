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
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
    private static final int PICK_IMAGE = 1;
    private static final int MAX_BYTES = 12 * 1024 * 1024;
    private static final long MAX_PIXELS = 32_000_000L;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private TextView result;
    private ImageView preview;
    private Button pick, sample;

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
        guidance.setText("Choose an image with one dark circle, triangle, or quadrilateral on a light background.");
        guidance.setTextColor(0xff30473f);
        guidance.setTextSize(16);
        guidance.setPadding(0, dp(8), 0, dp(16));
        page.addView(guidance);
        pick = new Button(this);
        pick.setText("Choose image");
        pick.setOnClickListener(view -> chooseImage());
        page.addView(pick);
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
            analyze(() -> image);
        });
        page.addView(sample);
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
    }

    private void chooseImage() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.setType("image/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.putExtra(Intent.EXTRA_LOCAL_ONLY, true);
        try {
            startActivityForResult(intent, PICK_IMAGE);
        } catch (android.content.ActivityNotFoundException error) {
            result.setText("No Android file picker is available.");
        }
    }

    @Override protected void onActivityResult(int request, int status, Intent data) {
        super.onActivityResult(request, status, data);
        if (request == PICK_IMAGE && status == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            analyze(() -> readImage(uri));
        }
    }

    private interface ImageSource {
        Bitmap get() throws IOException;
    }

    private void analyze(ImageSource source) {
        pick.setEnabled(false);
        sample.setEnabled(false);
        preview.setImageDrawable(null);
        result.setText("Analyzing image…");
        worker.execute(() -> {
            try {
                Bitmap bitmap = source.get();
                int w = bitmap.getWidth(), h = bitmap.getHeight();
                int[] pixels = new int[w * h];
                bitmap.getPixels(pixels, 0, w, 0, 0, w, h);
                String label = ShapeRecognizer.classify(pixels, w, h);
                show(bitmap, label);
            } catch (IOException | RuntimeException error) {
                show(null, "Could not read this image. Try a smaller JPEG or PNG.");
            }
        });
    }

    private void show(Bitmap bitmap, String message) {
        runOnUiThread(() -> {
            if (isDestroyed()) return;
            preview.setImageBitmap(bitmap);
            result.setText(message);
            pick.setEnabled(true);
            sample.setEnabled(true);
        });
    }

    private Bitmap readImage(Uri uri) throws IOException {
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
        return bitmap;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override protected void onDestroy() {
        worker.shutdownNow();
        super.onDestroy();
    }
}
