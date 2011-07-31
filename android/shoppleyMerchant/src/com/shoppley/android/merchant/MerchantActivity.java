package com.shoppley.android.merchant;

import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.util.Log;

/**
 * Combining a TabHost with a ViewPager to implement a tab UI that switches
 * between tabs and also allows the user to perform horizontal flicks to move
 * between the tabs.
 */
public class MerchantActivity extends FragmentActivity {

	MerchantFragment shoppleyFragment;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		setContentView(R.layout.fragment_stack);

		shoppleyFragment = new MerchantFragment();
		// newF.setRetainInstance(true);
		FragmentTransaction ft = getSupportFragmentManager().beginTransaction();
		ft.add(R.id.simple_fragment, shoppleyFragment);
		ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
		ft.commit();
		// mTabHost = (TabHost)findViewById(android.R.id.tabhost);
		// mTabHost.setup();
		//
		// mViewPager = (ViewPager)findViewById(R.id.pager);
		// mTabsAdapter = new TabsAdapter(this, mTabHost, mViewPager);
		// //TODO: Put String in XML
		// mTabsAdapter.addTab(mTabHost.newTabSpec("current").setIndicator("Current Offers",
		// getResources().getDrawable(R.drawable.tab_current_offers)),
		// CurrentListFragment.class, null);
		// mTabsAdapter.addTab(mTabHost.newTabSpec("redeemed").setIndicator("Redeemed Offers",
		// getResources().getDrawable(R.drawable.tab_redeemed_offers)),
		// RedeemedListFragment.class, null);
		// mTabsAdapter.addTab(mTabHost.newTabSpec("settings").setIndicator("Settings",
		// getResources().getDrawable(R.drawable.tab_settings)),
		// SettingsFragment.class, null);

		// if (savedInstanceState != null) {
		// mTabHost.setCurrentTabByTag(savedInstanceState.getString("tab"));
		// }
	}

	@Override
	public void onBackPressed() {
		// TODO Auto-generated method stub
		// Log.d("BACKPRESSED",""+getSupportFragmentManager().getBackStackEntryCount());
		super.onBackPressed();
		// FragmentTransaction ft =
		// getSupportFragmentManager().beginTransaction();
	}

	@Override
	protected void onResume() {
		//((MerchantApplication) getApplication()).requestLocationUpdate();
		super.onResume();
	}

	protected void onPause() {
		super.onPause();
		//((MerchantApplication) getApplication()).removeLocationUpdate();
	};
}
