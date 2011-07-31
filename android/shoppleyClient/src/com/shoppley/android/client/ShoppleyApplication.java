package com.shoppley.android.client;

import java.util.ArrayList;

import android.content.Context;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;

import com.github.droidfu.DroidFuApplication;
import com.higherpass.android.ContactAPI.ContactAPI;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;

public class ShoppleyApplication extends DroidFuApplication implements
		LocationListener {
	// Store global states across login and shoppley activities.
	private ShoppleyCustomerAPI api = new ShoppleyCustomerAPI();

	public ShoppleyCustomerAPI getAPI() {
		return api;
	}

	@Override
	public void onCreate() {
		// TODO Auto-generated method stub
		super.onCreate();
		locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
		// In order to make sure the device is getting the location, request
		// updates.

		capi = ContactAPI.getAPI();
		capi.setCr(getContentResolver());

		contactAdapter = new ArrayAdapter<String>(this,
				R.layout.forward_dropdown, clist);
	}

	private Location mostRecentLocation = null;
	private LocationManager locationManager;
	private ContactAPI capi = null;
	private ArrayList<String> clist = new ArrayList<String>();
	private ArrayAdapter<String> contactAdapter;

	public void requestLocationUpdate() {
		Criteria criteria = new Criteria();
		criteria.setAccuracy(Criteria.ACCURACY_FINE);
		String provider = locationManager.getBestProvider(criteria, true);
		if (provider != null) {
			locationManager.requestLocationUpdates(provider, 1, 0, this);
			mostRecentLocation = locationManager.getLastKnownLocation(provider);
		}
	}

	public void removeLocationUpdate() {
		Criteria criteria = new Criteria();
		criteria.setAccuracy(Criteria.ACCURACY_FINE);
		String provider = locationManager.getBestProvider(criteria, true);
		if (provider != null) {
			locationManager.removeUpdates(this);
		}
	}

	public Location getLocation() {
		return mostRecentLocation;
	}

	public void onLocationChanged(Location location) {
		// TODO Auto-generated method stub
		Log.d("location", location.toString());
		mostRecentLocation = location;
	}

	public void onProviderDisabled(String provider) {
		// TODO Auto-generated method stub

	}

	public void onProviderEnabled(String provider) {
		// TODO Auto-generated method stub

	}

	public void onStatusChanged(String provider, int status, Bundle extras) {
		// TODO Auto-generated method stub

	}

	public ContactAPI getContactAPI() {
		if (capi == null) {
			capi = ContactAPI.getAPI();
			capi.setCr(getContentResolver());
		}
		return capi;
	}

	public ArrayAdapter<String> getContactAdapter() {
		return contactAdapter;
	}
}