package com.sample.foo.tsgeocodeapp;

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
}
