package com.sample.foo.tsgeocodeapp;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import androidx.arch.core.executor.testing.InstantTaskExecutorRule;
import androidx.lifecycle.Observer;

import org.junit.Rule;
import org.junit.Test;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

public class GeocodeViewModelTest {
    @Rule
    public final InstantTaskExecutorRule instantTaskExecutorRule =
            new InstantTaskExecutorRule();

    @Test
    public void initialStateIsIdleWithoutAResult() {
        GeocodeViewModel viewModel = new GeocodeViewModel();

        GeocodeViewModel.UiState state = viewModel.getCurrentState();

        assertFalse(state.isRequestInFlight());
        assertNull(state.getDisplayMessage());
    }

    @Test
    public void onlyOneRequestCanBeInFlight() {
        GeocodeViewModel viewModel = new GeocodeViewModel();

        assertTrue(viewModel.beginRequest());
        assertFalse(viewModel.beginRequest());
        assertTrue(viewModel.getCurrentState().isRequestInFlight());
    }

    @Test
    public void successSettlesTheRequestAndFormatsTheAddress() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.completeResult(Constants.SUCCESS_RESULT, 37.422, -122.084,
                "1600 Amphitheatre Parkway");

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertEquals("Latitude: 37.422\nLongitude: -122.084\n" +
                "Address: 1600 Amphitheatre Parkway", state.getDisplayMessage());
    }

    @Test
    public void failureSettlesTheRequestWithItsMessage() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.completeResult(Constants.FAILURE_RESULT, null, null, "Not Found");

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertEquals("Not Found", state.getDisplayMessage());
    }

    @Test
    public void missingResultsUseTheSafeFallbackAndSettleTheRequest() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.completeResult(Constants.SUCCESS_RESULT, null, null, null);

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertEquals(GeocodeViewModel.NO_GEOCODE_RESULT, state.getDisplayMessage());
    }

    @Test
    public void successWithoutAnAddressUsesTheSafeFallback() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.completeResult(Constants.SUCCESS_RESULT, null, null, "Address text");

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertEquals(GeocodeViewModel.NO_GEOCODE_RESULT, state.getDisplayMessage());
    }

    @Test
    public void successWithInvalidCoordinatesUsesTheSafeFallback() {
        double[][] invalidCoordinates = {
                {Double.NaN, 0},
                {0, Double.POSITIVE_INFINITY},
                {-90.0001, 0},
                {90.0001, 0},
                {0, -180.0001},
                {0, 180.0001}
        };

        for (double[] coordinates : invalidCoordinates) {
            GeocodeViewModel viewModel = new GeocodeViewModel();
            viewModel.beginRequest();

            viewModel.completeResult(Constants.SUCCESS_RESULT,
                    coordinates[0], coordinates[1], "Address text");

            GeocodeViewModel.UiState state = viewModel.getCurrentState();
            assertFalse(state.isRequestInFlight());
            assertEquals(GeocodeViewModel.NO_GEOCODE_RESULT, state.getDisplayMessage());
        }
    }

    @Test
    public void emptyFailureMessageUsesTheSafeFallback() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.completeResult(Constants.FAILURE_RESULT, null, null, "");

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertEquals(GeocodeViewModel.NO_GEOCODE_RESULT, state.getDisplayMessage());
    }

    @Test
    public void cancelledStartupRestoresIdleStateWithoutInventingAResult() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        viewModel.beginRequest();

        viewModel.cancelRequest();

        GeocodeViewModel.UiState state = viewModel.getCurrentState();
        assertFalse(state.isRequestInFlight());
        assertNull(state.getDisplayMessage());
    }

    @Test
    public void liveDataPublishesEachRetainedStateTransition() {
        GeocodeViewModel viewModel = new GeocodeViewModel();
        List<GeocodeViewModel.UiState> observedStates = new ArrayList<>();
        Observer<GeocodeViewModel.UiState> observer = observedStates::add;
        viewModel.getUiState().observeForever(observer);

        viewModel.beginRequest();
        viewModel.completeResult(Constants.FAILURE_RESULT, null, null, "Not Found");

        viewModel.getUiState().removeObserver(observer);
        assertEquals(3, observedStates.size());
        assertFalse(observedStates.get(0).isRequestInFlight());
        assertTrue(observedStates.get(1).isRequestInFlight());
        assertEquals("Not Found", observedStates.get(2).getDisplayMessage());
    }

    @Test
    public void retainedStateOwnsNoUiObjectFields() {
        for (Field field : GeocodeViewModel.class.getDeclaredFields()) {
            String fieldType = field.getType().getName();
            assertFalse(fieldType, fieldType.startsWith("android.app."));
            assertFalse(fieldType, fieldType.startsWith("android.view."));
            assertFalse(fieldType, fieldType.equals("android.content.Context"));
        }
    }
}
