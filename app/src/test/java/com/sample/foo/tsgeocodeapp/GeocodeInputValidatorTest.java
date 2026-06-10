package com.sample.foo.tsgeocodeapp;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class GeocodeInputValidatorTest {
    @Test
    public void normalizeAddressTrimsInput() {
        assertEquals("1600 Amphitheatre Parkway",
                GeocodeInputValidator.normalizeAddress("  1600 Amphitheatre Parkway  "));
    }

    @Test
    public void normalizeAddressHandlesMissingInput() {
        assertEquals("", GeocodeInputValidator.normalizeAddress(null));
    }

    @Test
    public void coordinatesIncludeGeographicBoundaries() {
        assertTrue(GeocodeInputValidator.isCoordinateInRange(-90, -180));
        assertTrue(GeocodeInputValidator.isCoordinateInRange(90, 180));
    }

    @Test
    public void coordinatesRejectValuesOutsideGeographicBoundaries() {
        assertFalse(GeocodeInputValidator.isCoordinateInRange(-90.0001, 0));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(90.0001, 0));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(0, -180.0001));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(0, 180.0001));
    }

    @Test
    public void coordinatesRejectNonFiniteValues() {
        assertFalse(GeocodeInputValidator.isCoordinateInRange(Double.NaN, 0));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(0, Double.NaN));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(Double.POSITIVE_INFINITY, 0));
        assertFalse(GeocodeInputValidator.isCoordinateInRange(0, Double.NEGATIVE_INFINITY));
    }
}
