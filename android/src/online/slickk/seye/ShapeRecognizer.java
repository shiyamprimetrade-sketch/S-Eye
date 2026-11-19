package online.slickk.seye;

import java.util.ArrayList;
import java.util.List;

/** Classifies a single dark, outlined or filled shape on a light background. */
public final class ShapeRecognizer {
    public static final String UNKNOWN = "Unknown";
    public static final int MAX_SIDE = 768;

    private ShapeRecognizer() {}

    private static final class Point {
        final int x, y;
        Point(int x, int y) { this.x = x; this.y = y; }
    }

    public static String classify(int[] argb, int width, int height) {
        if (width < 16 || height < 16 || width > MAX_SIDE || height > MAX_SIDE
                || argb.length != width * height)
            return UNKNOWN;
        List<Point> extremes = new ArrayList<>();
        int count = 0, top = height, bottom = -1, left = width, right = -1;
        for (int x = 0; x < width; x++) {
            int first = height, last = -1;
            for (int y = 0; y < height; y++) {
                if (!dark(argb[y * width + x])) continue;
                first = Math.min(first, y);
                last = y;
                count++;
            }
            if (last < 0) continue;
            extremes.add(new Point(x, first));
            if (first != last) extremes.add(new Point(x, last));
            top = Math.min(top, first);
            bottom = Math.max(bottom, last);
            left = Math.min(left, x);
            right = x;
        }
        if (count < 48 || right - left < 15 || bottom - top < 15
                || left == 0 || top == 0 || right == width - 1 || bottom == height - 1)
            return UNKNOWN;
        double span = Math.max(right - left, bottom - top);
        List<Point> hull = convexHull(extremes);
        double area = 0, perimeter = 0;
        for (int i = 0; i < hull.size(); i++) {
            Point a = hull.get(i), b = hull.get((i + 1) % hull.size());
            area += a.x * b.y - a.y * b.x;
            perimeter += Math.hypot(a.x - b.x, a.y - b.y);
        }
        area = Math.abs(area) / 2;
        if (area < span * span * .16) return UNKNOWN;
        if (count / area < .85) {
            int near = 0;
            double tolerance = span * .15;
            for (int y = top; y <= bottom; y++) {
                for (int x = left; x <= right; x++) {
                    if (!dark(argb[y * width + x])) continue;
                    for (int i = 0; i < hull.size(); i++) {
                        Point a = hull.get(i), b = hull.get((i + 1) % hull.size());
                        if (Math.abs(cross(a, b, x, y))
                                <= tolerance * Math.hypot(a.x - b.x, a.y - b.y)) {
                            near++;
                            break;
                        }
                    }
                }
            }
            if (near < .83 * count) return UNKNOWN;
        }
        List<Point> outline = new ArrayList<>(hull);
        double tolerance = span * .045;
        while (outline.size() > 3) {
            double deviation = Double.POSITIVE_INFINITY;
            int remove = -1;
            for (int i = 0; i < outline.size(); i++) {
                Point a = outline.get((i + outline.size() - 1) % outline.size());
                Point p = outline.get(i);
                Point b = outline.get((i + 1) % outline.size());
                double d = Math.abs(cross(a, b, p.x, p.y)) / Math.hypot(a.x-b.x, a.y-b.y);
                if (d < deviation) { deviation = d; remove = i; }
            }
            if (deviation > tolerance) break;
            outline.remove(remove);
        }
        double circularity = 4 * Math.PI * area / (perimeter * perimeter);
        if (circularity >= .89 && Math.min(right-left, bottom-top) >= .84 * span)
            return "Circle";
        if (outline.size() == 3) return "Triangle";
        if (outline.size() == 4 && circularity <= .86) return "Quadrilateral";
        return UNKNOWN;
    }

    private static boolean dark(int pixel) {
        if ((pixel >>> 24) < 128) return false;
        int luma = 299 * ((pixel >>> 16) & 255) + 587 * ((pixel >>> 8) & 255) + 114 * (pixel & 255);
        return luma < 128000;
    }

    private static int cross(Point a, Point b, int x, int y) {
        return (b.x-a.x)*(y-a.y) - (b.y-a.y)*(x-a.x);
    }

    private static List<Point> convexHull(List<Point> sorted) {
        List<Point> hull = new ArrayList<>();
        for (Point p : sorted) appendHull(hull, p, 0);
        int lower = hull.size() - 1;
        for (int i = sorted.size() - 2; i >= 0; i--) appendHull(hull, sorted.get(i), lower);
        hull.remove(hull.size() - 1);
        return hull;
    }

    private static void appendHull(List<Point> hull, Point p, int start) {
        while (hull.size() - start >= 2) {
            int n = hull.size();
            if (cross(hull.get(n-2), hull.get(n-1), p.x, p.y) > 0) break;
            hull.remove(n-1);
        }
        hull.add(p);
    }
}
