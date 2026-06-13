package com.sample.foo.tsgeocodeapp;

import java.lang.ref.WeakReference;

import android.content.Intent;
import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ResultReceiver;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    AddressResultReceiver mResultReceiver;

    EditText latitudeEdit, longitudeEdit, addressEdit;
    ProgressBar progressBar;
    TextView infoText;

    private static final String TAG = "MAIN_ACTIVITY";
    private static final String NO_GEOCODE_RESULT = "No geocode result";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        longitudeEdit = (EditText) findViewById(R.id.longitudeEdit);
        latitudeEdit = (EditText) findViewById(R.id.latitudeEdit);
        addressEdit = (EditText) findViewById(R.id.addressEdit);
        progressBar = (ProgressBar) findViewById(R.id.progressBar);
        infoText = (TextView) findViewById(R.id.infoText);

        findViewById(R.id.radioAddress).setOnClickListener(this::onRadioButtonClicked);
        findViewById(R.id.radioLocation).setOnClickListener(this::onRadioButtonClicked);
        ((Button) findViewById(R.id.actionButton)).setOnClickListener(this::onButtonClicked);

        mResultReceiver = new AddressResultReceiver(this);
    }

    public void onRadioButtonClicked(View view) {
        boolean checked = ((RadioButton) view).isChecked();

        if (view.getId() == R.id.radioAddress && checked) {
            longitudeEdit.setEnabled(false);
            latitudeEdit.setEnabled(false);
            addressEdit.setEnabled(true);
            addressEdit.requestFocus();
        } else if (view.getId() == R.id.radioLocation && checked) {
            latitudeEdit.setEnabled(true);
            latitudeEdit.requestFocus();
            longitudeEdit.setEnabled(true);
            addressEdit.setEnabled(false);
        }
    }

    public void onButtonClicked(View view) {
        int fetchType = ((RadioButton) findViewById(R.id.radioAddress)).isChecked()
                ? Constants.USE_ADDRESS_NAME
                : Constants.USE_ADDRESS_LOCATION;
        Intent intent = new Intent(this, GeocodeAddressIntentService.class);
        intent.putExtra(Constants.RECEIVER, mResultReceiver);
        intent.putExtra(Constants.FETCH_TYPE_EXTRA, fetchType);
        if(fetchType == Constants.USE_ADDRESS_NAME) {
            String addressName = GeocodeInputValidator.normalizeAddress(
                    addressEdit.getText().toString());
            if(addressName.length() == 0) {
                Toast.makeText(this, "Please enter an address name", Toast.LENGTH_LONG).show();
                return;
            }
            intent.putExtra(Constants.LOCATION_NAME_DATA_EXTRA, addressName);
        }
        else {
            if(latitudeEdit.getText().length() == 0 || longitudeEdit.getText().length() == 0) {
                Toast.makeText(this,
                        "Please enter both latitude and longitude",
                        Toast.LENGTH_LONG).show();
                return;
            }
            double latitude;
            double longitude;
            try {
                latitude = Double.parseDouble(latitudeEdit.getText().toString());
                longitude = Double.parseDouble(longitudeEdit.getText().toString());
            } catch (NumberFormatException numberFormatException) {
                Toast.makeText(this,
                        R.string.invalid_latitude_longitude,
                        Toast.LENGTH_LONG).show();
                return;
            }
            if(!isCoordinateInRange(latitude, longitude)) {
                Toast.makeText(this,
                        R.string.invalid_latitude_longitude,
                        Toast.LENGTH_LONG).show();
                return;
            }
            intent.putExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA,
                    latitude);
            intent.putExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA,
                    longitude);
        }
        if (!Geocoder.isPresent()) {
            progressBar.setVisibility(View.GONE);
            Toast.makeText(this, R.string.geocoder_unavailable, Toast.LENGTH_LONG).show();
            return;
        }
        infoText.setVisibility(View.INVISIBLE);
        progressBar.setVisibility(View.VISIBLE);
        Log.e(TAG, "Starting Service");
        startService(intent);
    }

    private boolean isCoordinateInRange(double latitude, double longitude) {
        return GeocodeInputValidator.isCoordinateInRange(latitude, longitude);
    }

    private static final class AddressResultReceiver extends ResultReceiver {
        private final WeakReference<MainActivity> activityReference;

        AddressResultReceiver(MainActivity activity) {
            super(new Handler(Looper.getMainLooper()));
            activityReference = new WeakReference<>(activity);
        }

        @Override
        protected void onReceiveResult(int resultCode, final Bundle resultData) {
            MainActivity activity = activityReference.get();
            if (activity == null || activity.isFinishing() || activity.isDestroyed()) {
                return;
            }

            activity.handleGeocodeResult(resultCode, resultData);
        }
    }

    private void handleGeocodeResult(int resultCode, Bundle resultData) {
        if (resultData == null) {
            showResultText(NO_GEOCODE_RESULT);
            return;
        }

        final String resultMessage = resultData.getString(Constants.RESULT_DATA_KEY);
        if (resultCode == Constants.SUCCESS_RESULT) {
            final Address address = resultData.getParcelable(Constants.RESULT_ADDRESS);
            if (address == null || TextUtils.isEmpty(resultMessage)) {
                showResultText(NO_GEOCODE_RESULT);
                return;
            }

            showResultText("Latitude: " + address.getLatitude() + "\n" +
                    "Longitude: " + address.getLongitude() + "\n" +
                    "Address: " + resultMessage);
        }
        else {
            showResultText(TextUtils.isEmpty(resultMessage) ?
                    NO_GEOCODE_RESULT : resultMessage);
        }
    }

    private void showResultText(final String message) {
        progressBar.setVisibility(View.GONE);
        infoText.setVisibility(View.VISIBLE);
        infoText.setText(message);
    }

}
