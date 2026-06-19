package com.sample.foo.tsgeocodeapp;

import android.app.IntentService;
import android.content.Intent;
import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;
import android.os.ResultReceiver;
import android.text.TextUtils;
import android.util.Log;

import androidx.core.content.IntentCompat;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class GeocodeAddressIntentService extends IntentService {

    protected ResultReceiver resultReceiver;
    private static final String TAG = "GEO_ADDY_SERVICE";

    public GeocodeAddressIntentService() {
        super("GeocodeAddressIntentService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        Log.e(TAG, "onHandleIntent");
        String errorMessage = "";
        List<Address> addresses = null;

        resultReceiver = IntentCompat.getParcelableExtra(
                intent,
                Constants.RECEIVER,
                ResultReceiver.class);
        if (resultReceiver == null) {
            Log.e(TAG, "Missing ResultReceiver");
            return;
        }
        if (!Geocoder.isPresent()) {
            errorMessage = getString(R.string.geocoder_unavailable);
            Log.e(TAG, "Geocoder unavailable");
            deliverResultToReceiver(Constants.FAILURE_RESULT, errorMessage, null);
            return;
        }

        Geocoder geocoder = new Geocoder(this, Locale.getDefault());

        int fetchType = intent.getIntExtra(Constants.FETCH_TYPE_EXTRA, 0);
        Log.e(TAG, "fetchType == " + fetchType);

        if(fetchType == Constants.USE_ADDRESS_NAME) {
            String name = intent.getStringExtra(Constants.LOCATION_NAME_DATA_EXTRA);
            name = GeocodeInputValidator.normalizeAddress(name);
            if(TextUtils.isEmpty(name)) {
                errorMessage = "Invalid Address Name";
                Log.e(TAG, errorMessage);
            } else {
                try {
                    addresses = geocoder.getFromLocationName(name, 1);
                } catch (IOException e) {
                    errorMessage = "Service not available";
                    Log.e(TAG, errorMessage, e);
                }
            }
        }
        else if(fetchType == Constants.USE_ADDRESS_LOCATION) {
            double latitude = intent.getDoubleExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA, 0);
            double longitude = intent.getDoubleExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA, 0);

            if(!isCoordinateInRange(latitude, longitude)) {
                errorMessage = "Invalid Latitude or Longitude Used";
                Log.e(TAG, errorMessage);
            } else {
                try {
                    addresses = geocoder.getFromLocation(latitude, longitude, 1);
                } catch (IOException ioException) {
                    errorMessage = "Service Not Available";
                    Log.e(TAG, errorMessage, ioException);
                } catch (IllegalArgumentException illegalArgumentException) {
                    errorMessage = "Invalid Latitude or Longitude Used";
                    Log.e(TAG, errorMessage, illegalArgumentException);
                }
            }
        }
        else {
            errorMessage = "Unknown Type";
            Log.e(TAG, errorMessage);
        }

        if (addresses == null || addresses.size()  == 0) {
            if (errorMessage.isEmpty()) {
                errorMessage = "Not Found";
                Log.e(TAG, errorMessage);
            }
            deliverResultToReceiver(Constants.FAILURE_RESULT, errorMessage, null);
        } else {
            Address address = addresses.get(0);
            ArrayList<String> addressFragments = new ArrayList<>();

            for(int i = 0; i <= address.getMaxAddressLineIndex(); i++) {
                addressFragments.add(address.getAddressLine(i));
            }
            Log.i(TAG, "Address Found");
            deliverResultToReceiver(Constants.SUCCESS_RESULT,
                    TextUtils.join(System.getProperty("line.separator"),
                            addressFragments), address);
        }
    }

    private boolean isCoordinateInRange(double latitude, double longitude) {
        return GeocodeInputValidator.isCoordinateInRange(latitude, longitude);
    }

    private void deliverResultToReceiver(int resultCode, String message, Address address) {
        Bundle bundle = new Bundle();
        bundle.putParcelable(Constants.RESULT_ADDRESS, address);
        bundle.putString(Constants.RESULT_DATA_KEY, message);
        resultReceiver.send(resultCode, bundle);
    }

}
