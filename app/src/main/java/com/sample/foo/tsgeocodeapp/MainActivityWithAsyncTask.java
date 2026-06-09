package com.sample.foo.tsgeocodeapp;

import android.location.Address;
import android.location.Geocoder;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

public class MainActivityWithAsyncTask extends AppCompatActivity {

    EditText latitudeEdit, longitudeEdit, addressEdit;
    ProgressBar progressBar;
    TextView infoText;
    CheckBox checkBox;

    public static final int USE_ADDRESS_NAME = 1;
    public static final int USE_ADDRESS_LOCATION = 2;

    int fetchType = USE_ADDRESS_LOCATION;

    private static final String TAG = "MAIN_ACTIVITY_ASYNC";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        longitudeEdit = (EditText) findViewById(R.id.longitudeEdit);
        latitudeEdit = (EditText) findViewById(R.id.latitudeEdit);
        addressEdit = (EditText) findViewById(R.id.addressEdit);
        progressBar = (ProgressBar) findViewById(R.id.progressBar);
        infoText = (TextView) findViewById(R.id.infoText);
        checkBox = (CheckBox) findViewById(R.id.checkbox);
    }

    public void onRadioButtonClicked(View view) {
        boolean checked = ((RadioButton) view).isChecked();

        switch(view.getId()) {
            case R.id.radioAddress:
                if (checked) {
                    fetchType = USE_ADDRESS_NAME;
                    longitudeEdit.setEnabled(false);
                    latitudeEdit.setEnabled(false);
                    addressEdit.setEnabled(true);
                    addressEdit.requestFocus();
                }
                break;
            case R.id.radioLocation:
                if (checked) {
                    fetchType = USE_ADDRESS_LOCATION;
                    latitudeEdit.setEnabled(true);
                    latitudeEdit.requestFocus();
                    longitudeEdit.setEnabled(true);
                    addressEdit.setEnabled(false);
                }
                break;
        }
    }

    public void onButtonClicked(View view) {
        if(fetchType == USE_ADDRESS_NAME) {
            String addressName = addressEdit.getText().toString().trim();
            if(addressName.length() == 0) {
                Toast.makeText(this, "Please enter an address name", Toast.LENGTH_LONG).show();
                return;
            }
            new GeocodeAsyncTask(fetchType, addressName, 0, 0).execute();
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
            new GeocodeAsyncTask(fetchType, null, latitude, longitude).execute();
        }
    }

    class GeocodeAsyncTask extends AsyncTask<Void, Void, Address> {

        final int taskFetchType;
        final String addressName;
        final double latitude;
        final double longitude;
        String errorMessage = "";

        GeocodeAsyncTask(int taskFetchType, String addressName, double latitude, double longitude) {
            this.taskFetchType = taskFetchType;
            this.addressName = addressName;
            this.latitude = latitude;
            this.longitude = longitude;
        }

        @Override
        protected void onPreExecute() {
            infoText.setVisibility(View.INVISIBLE);
            progressBar.setVisibility(View.VISIBLE);
        }

        @Override
        protected Address doInBackground(Void ... none) {
            Geocoder geocoder = new Geocoder(MainActivityWithAsyncTask.this, Locale.getDefault());
            List<Address> addresses = null;

            if(taskFetchType == USE_ADDRESS_NAME) {
                try {
                    addresses = geocoder.getFromLocationName(addressName, 1);
                } catch (IOException e) {
                    errorMessage = "Service not available";
                    Log.e(TAG, errorMessage, e);
                }
            }
            else if(taskFetchType == USE_ADDRESS_LOCATION) {
                try {
                    addresses = geocoder.getFromLocation(latitude, longitude, 1);
                } catch (IOException ioException) {
                    errorMessage = "Service Not Available";
                    Log.e(TAG, errorMessage, ioException);
                } catch (IllegalArgumentException illegalArgumentException) {
                    errorMessage = "Invalid Latitude or Longitude Used";
                    Log.e(TAG, errorMessage + ". " +
                            "Latitude = " + latitude + ", Longitude = " +
                            longitude, illegalArgumentException);
                }
            }
            else {
                errorMessage = "Unknown Type";
                Log.e(TAG, errorMessage);
            }

            if(addresses != null && addresses.size() > 0)
                return addresses.get(0);

            return null;
        }

        protected void onPostExecute(Address address) {
            if(address == null) {
                progressBar.setVisibility(View.INVISIBLE);
                infoText.setVisibility(View.VISIBLE);
                infoText.setText(errorMessage);
            }
            else {
                String addressName = "";
                for(int i = 0; i < address.getMaxAddressLineIndex(); i++) {
                    addressName += " --- " + address.getAddressLine(i);
                }
                progressBar.setVisibility(View.INVISIBLE);
                infoText.setVisibility(View.VISIBLE);
                infoText.setText("Latitude: " + address.getLatitude() + "\n" +
                        "Longitude: " + address.getLongitude() + "\n" +
                        "Address: " + addressName);
            }
        }
    }
}
