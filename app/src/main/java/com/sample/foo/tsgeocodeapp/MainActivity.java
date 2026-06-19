package com.sample.foo.tsgeocodeapp;

import android.content.Intent;
import android.location.Geocoder;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;

public class MainActivity extends AppCompatActivity {

    GeocodeViewModel geocodeViewModel;

    EditText latitudeEdit, longitudeEdit, addressEdit;
    Button actionButton;
    ProgressBar progressBar;
    TextView infoText;

    private static final String TAG = "MAIN_ACTIVITY";
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
        actionButton = (Button) findViewById(R.id.actionButton);
        actionButton.setOnClickListener(this::onButtonClicked);

        geocodeViewModel = new ViewModelProvider(this).get(GeocodeViewModel.class);
        geocodeViewModel.getUiState().observe(this, this::renderUiState);
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
        if (!geocodeViewModel.beginRequest()) {
            return;
        }
        try {
            intent.putExtra(Constants.RECEIVER, geocodeViewModel.getResultReceiver());
            Log.e(TAG, "Starting Service");
            startService(intent);
        } catch (RuntimeException runtimeException) {
            geocodeViewModel.cancelRequest();
            throw runtimeException;
        }
    }

    private boolean isCoordinateInRange(double latitude, double longitude) {
        return GeocodeInputValidator.isCoordinateInRange(latitude, longitude);
    }

    private void renderUiState(GeocodeViewModel.UiState state) {
        boolean requestInFlight = state.isRequestInFlight();
        progressBar.setVisibility(requestInFlight ? View.VISIBLE : View.GONE);
        actionButton.setEnabled(!requestInFlight);

        String displayMessage = state.getDisplayMessage();
        if (displayMessage != null) {
            infoText.setVisibility(View.VISIBLE);
            infoText.setText(displayMessage);
        } else {
            infoText.setVisibility(requestInFlight ? View.INVISIBLE : View.VISIBLE);
        }
    }

}
