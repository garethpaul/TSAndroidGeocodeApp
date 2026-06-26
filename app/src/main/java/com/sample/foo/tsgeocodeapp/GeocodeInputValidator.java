package com.sample.foo.tsgeocodeapp;

import java.util.List;

final class GeocodeInputValidator {
    private GeocodeInputValidator() {
    }

    static String normalizeAddress(String address) {
        return address == null ? "" : address.trim();
    }

    static boolean isCoordinateInRange(double latitude, double longitude) {
        return Double.isFinite(latitude)
                && Double.isFinite(longitude)
                && latitude >= -90
                && latitude <= 90
                && longitude >= -180
                && longitude <= 180;
    }

    static String formatAddressLines(List<String> addressLines, String separator) {
        if (addressLines == null) {
            return "";
        }

        String delimiter = separator == null ? "" : separator;
        StringBuilder formattedAddress = new StringBuilder();
        for (String addressLine : addressLines) {
            String normalizedLine = normalizeAddress(addressLine);
            if (normalizedLine.isEmpty()) {
                continue;
            }
            if (formattedAddress.length() > 0) {
                formattedAddress.append(delimiter);
            }
            formattedAddress.append(normalizedLine);
        }
        return formattedAddress.toString();
    }
}
