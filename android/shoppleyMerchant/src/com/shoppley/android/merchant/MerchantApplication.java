package com.shoppley.android.merchant;

import com.github.droidfu.DroidFuApplication;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;

public class MerchantApplication extends DroidFuApplication {
	// Store global states across login and shoppley activities.
	private ShoppleyMerchantAPI api = new ShoppleyMerchantAPI();

	public ShoppleyMerchantAPI getAPI() {
		return api;
	}

	@Override
	public void onCreate() {
		// TODO Auto-generated method stub
		super.onCreate();
		//locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
		// In order to make sure the device is getting the location, request
		// updates.

	}

	// private Location mostRecentLocation = null;
	// private LocationManager locationManager;
//
//	public void requestLocationUpdate() {
//		Criteria criteria = new Criteria();
//		criteria.setAccuracy(Criteria.ACCURACY_FINE);
//		String provider = locationManager.getBestProvider(criteria, true);
//		if (provider != null) {
//			locationManager.requestLocationUpdates(provider, 1, 0, this);
//			mostRecentLocation = locationManager.getLastKnownLocation(provider);
//		}
//	}
//
//	public void removeLocationUpdate() {
//		Criteria criteria = new Criteria();
//		criteria.setAccuracy(Criteria.ACCURACY_FINE);
//		String provider = locationManager.getBestProvider(criteria, true);
//		if (provider != null) {
//			locationManager.removeUpdates(this);
//		}
//	}
//
//	public Location getLocation() {
//		return mostRecentLocation;
//	}
//
//	public void onLocationChanged(Location location) {
//		// TODO Auto-generated method stub
//		Log.d("location", location.toString());
//		mostRecentLocation = location;
//	}
//
//	public void onProviderDisabled(String provider) {
//		// TODO Auto-generated method stub
//
//	}
//
//	public void onProviderEnabled(String provider) {
//		// TODO Auto-generated method stub
//
//	}
//
//	public void onStatusChanged(String provider, int status, Bundle extras) {
//		// TODO Auto-generated method stub
//
//	}

}