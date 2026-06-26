package com.fleetingjobs.util;

import java.text.Normalizer;
import java.util.Locale;
import java.util.regex.Pattern;

public final class SlugUtils {

    private static final Pattern NON_ALNUM = Pattern.compile("[^a-zA-Z0-9]+");

    private SlugUtils() {
    }

    public static String slugify(String value) {
        String normalized = Normalizer.normalize(value, Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "");
        String slug = NON_ALNUM.matcher(normalized).replaceAll("-").replaceAll("^-|-$", "").toLowerCase(Locale.ROOT);
        return slug.isBlank() ? "company" : slug;
    }
}
