package com.shoppley.android.client;

import android.os.Bundle;
import android.support.v4.app.FragmentActivity;

public class CurrentActivity extends FragmentActivity {
	// int mStackLevel = 1;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		// setContentView(R.layout.fragment_stack);
		//
		// if (savedInstanceState == null) {
		// CurrentOffer offer = (Offer)getIntent().getExtras()
		// .getSerializable(CurrentOffer.CURRENT_OFFER);
		// // Do first time initialization -- add initial fragment.
		// Fragment newFragment = CurrentFragment.newInstance(offer);
		// FragmentTransaction ft = getSupportFragmentManager()
		// .beginTransaction();
		// ft.add(R.id.simple_fragment, newFragment).commit();
		// } else {
		// // mStackLevel = savedInstanceState.getInt("level");
		// }
	}

	@Override
	public void onSaveInstanceState(Bundle outState) {
		super.onSaveInstanceState(outState);
		// outState.putInt("level", mStackLevel);
	}

}
