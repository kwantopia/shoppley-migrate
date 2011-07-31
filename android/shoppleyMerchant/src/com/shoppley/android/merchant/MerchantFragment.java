package com.shoppley.android.merchant;

import java.util.ArrayList;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TabHost;

import com.shoppley.android.utils.Utils;

/**
 * Combining a TabHost with a ViewPager to implement a tab UI that switches
 * between tabs and also allows the user to perform horizontal flicks to move
 * between the tabs.
 */
public class MerchantFragment extends Fragment {
	TabHost mTabHost;
	ViewPager mViewPager;
	TabsAdapter mTabsAdapter;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		View v = inflater.inflate(R.layout.tabs, container, false);
		mTabHost = (TabHost) v.findViewById(android.R.id.tabhost);
		mTabHost.setup();

		mViewPager = (ViewPager) v.findViewById(R.id.pager);
		mTabsAdapter = new TabsAdapter(getActivity(), mTabHost, mViewPager);
		mTabsAdapter.addTab(
				mTabHost.newTabSpec("active").setIndicator(
						"Active Offers",
						getResources()
								.getDrawable(R.drawable.tab_active_offers)),
				ActiveListFragment.class, null);
		mTabsAdapter
				.addTab(mTabHost.newTabSpec("past").setIndicator("Past Offers",
						getResources().getDrawable(R.drawable.tab_past_offers)),
						PastListFragment.class, null);
		mTabsAdapter.addTab(
				mTabHost.newTabSpec("redeem").setIndicator("Redeem",
						getResources().getDrawable(R.drawable.tab_redeem)),
				RedeemFragment.class, null);
		mTabsAdapter.addTab(
				mTabHost.newTabSpec("summary").setIndicator("Summary",
						getResources().getDrawable(R.drawable.tab_summary)),
				SummaryFragment.class, null);
		mTabsAdapter.addTab(
				mTabHost.newTabSpec("settings").setIndicator("Settings",
						getResources().getDrawable(R.drawable.tab_settings)),
				SettingsFragment.class, null);

		return v;
	}

	/**
	 * This is a helper class that implements the management of tabs and all
	 * details of connecting a ViewPager with associated TabHost. It relies on a
	 * trick. Normally a tab host has a simple API for supplying a View or
	 * Intent that each tab will show. This is not sufficient for switching
	 * between pages. So instead we make the content part of the tab host 0dp
	 * high (it is not shown) and the TabsAdapter supplies its own dummy view to
	 * show as the tab content. It listens to changes in tabs, and takes care of
	 * switch to the correct paged in the ViewPager whenever the selected tab
	 * changes.
	 */
	public static class TabsAdapter extends FragmentPagerAdapter implements
			TabHost.OnTabChangeListener, ViewPager.OnPageChangeListener {
		private final Context mContext;
		private final TabHost mTabHost;
		private final ViewPager mViewPager;
		private final ArrayList<TabInfo> mTabs = new ArrayList<TabInfo>();

		static final class TabInfo {
			private final String tag;
			private final Class<?> clss;
			private final Bundle args;

			TabInfo(String _tag, Class<?> _class, Bundle _args) {
				tag = _tag;
				clss = _class;
				args = _args;
			}
		}

		static class DummyTabFactory implements TabHost.TabContentFactory {
			private final Context mContext;

			public DummyTabFactory(Context context) {
				mContext = context;
			}

			public View createTabContent(String tag) {
				View v = new View(mContext);
				v.setMinimumWidth(0);
				v.setMinimumHeight(0);
				return v;
			}
		}

		public TabsAdapter(FragmentActivity activity, TabHost tabHost,
				ViewPager pager) {
			super(activity.getSupportFragmentManager());
			mContext = activity;
			mTabHost = tabHost;
			mViewPager = pager;
			mTabHost.setOnTabChangedListener(this);
			mViewPager.setAdapter(this);
			mViewPager.setOnPageChangeListener(this);
		}

		public void addTab(TabHost.TabSpec tabSpec, Class<?> clss, Bundle args) {
			tabSpec.setContent(new DummyTabFactory(mContext));
			String tag = tabSpec.getTag();

			TabInfo info = new TabInfo(tag, clss, args);
			mTabs.add(info);
			mTabHost.addTab(tabSpec);
			notifyDataSetChanged();
		}

		@Override
		public int getCount() {
			return mTabs.size();
		}

		@Override
		public Fragment getItem(int position) {
			TabInfo info = mTabs.get(position);
			Fragment instance = Fragment.instantiate(mContext,
					info.clss.getName(), info.args);
			return instance;
		}

		public void onTabChanged(String tabId) {
			Utils.hideKeyboard(mContext, mTabHost.getWindowToken());
			int position = mTabHost.getCurrentTab();
			mViewPager.setCurrentItem(position);
		}

		public void onPageScrolled(int position, float positionOffset,
				int positionOffsetPixels) {
		}

		public void onPageSelected(int position) {
			mTabHost.setCurrentTab(position);
		}

		public void onPageScrollStateChanged(int state) {
		}
	}

	// @Override
	// public void onBackPressed() {
	// // TODO Auto-generated method stub
	// //super.onBackPressed();
	// }
}
