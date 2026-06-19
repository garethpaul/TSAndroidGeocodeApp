package com.sample.foo.tsgeocodeapp;

import java.lang.ref.WeakReference;

import android.location.Address;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ResultReceiver;

import androidx.core.os.BundleCompat;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public final class GeocodeViewModel extends ViewModel {
    static final String NO_GEOCODE_RESULT = "No geocode result";

    private final MutableLiveData<UiState> uiState =
            new MutableLiveData<>(UiState.idle());
    private ResultReceiver resultReceiver;

    LiveData<UiState> getUiState() {
        return uiState;
    }

    UiState getCurrentState() {
        UiState state = uiState.getValue();
        if (state == null) {
            throw new IllegalStateException("Geocode UI state is not initialized");
        }
        return state;
    }

    boolean beginRequest() {
        UiState state = getCurrentState();
        if (state.isRequestInFlight()) {
            return false;
        }

        publish(new UiState(true, state.getDisplayMessage()));
        return true;
    }

    void cancelRequest() {
        publish(new UiState(false, getCurrentState().getDisplayMessage()));
    }

    void completeResult(int resultCode, Double latitude, Double longitude, String message) {
        if (resultCode == Constants.SUCCESS_RESULT
                && latitude != null
                && longitude != null
                && !isEmpty(message)) {
            completeSuccess(latitude, longitude, message);
        } else {
            completeFailure(resultCode == Constants.SUCCESS_RESULT ? null : message);
        }
    }

    private void completeSuccess(double latitude, double longitude, String addressText) {
        if (isEmpty(addressText)) {
            completeFailure(null);
            return;
        }

        publish(new UiState(false, "Latitude: " + latitude + "\n" +
                "Longitude: " + longitude + "\n" +
                "Address: " + addressText));
    }

    private void completeFailure(String message) {
        publish(new UiState(false, isEmpty(message) ? NO_GEOCODE_RESULT : message));
    }

    ResultReceiver getResultReceiver() {
        if (resultReceiver == null) {
            resultReceiver = new AddressResultReceiver(this);
        }
        return resultReceiver;
    }

    private void handleGeocodeResult(int resultCode, Bundle resultData) {
        if (resultData == null) {
            completeResult(resultCode, null, null, null);
            return;
        }

        String resultMessage = resultData.getString(Constants.RESULT_DATA_KEY);
        if (resultCode == Constants.SUCCESS_RESULT) {
            Address address = BundleCompat.getParcelable(
                    resultData,
                    Constants.RESULT_ADDRESS,
                    Address.class);
            completeResult(
                    resultCode,
                    address == null ? null : address.getLatitude(),
                    address == null ? null : address.getLongitude(),
                    resultMessage);
        } else {
            completeResult(resultCode, null, null, resultMessage);
        }
    }

    private void publish(UiState state) {
        uiState.setValue(state);
    }

    private static boolean isEmpty(String value) {
        return value == null || value.length() == 0;
    }

    private static final class AddressResultReceiver extends ResultReceiver {
        private final WeakReference<GeocodeViewModel> viewModelReference;

        AddressResultReceiver(GeocodeViewModel viewModel) {
            super(new Handler(Looper.getMainLooper()));
            viewModelReference = new WeakReference<>(viewModel);
        }

        @Override
        protected void onReceiveResult(int resultCode, Bundle resultData) {
            GeocodeViewModel viewModel = viewModelReference.get();
            if (viewModel != null) {
                viewModel.handleGeocodeResult(resultCode, resultData);
            }
        }
    }

    static final class UiState {
        private final boolean requestInFlight;
        private final String displayMessage;

        private UiState(boolean requestInFlight, String displayMessage) {
            this.requestInFlight = requestInFlight;
            this.displayMessage = displayMessage;
        }

        static UiState idle() {
            return new UiState(false, null);
        }

        boolean isRequestInFlight() {
            return requestInFlight;
        }

        String getDisplayMessage() {
            return displayMessage;
        }
    }
}
