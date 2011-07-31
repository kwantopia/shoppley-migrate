package com.shoppley.android.client;

import java.util.List;

import android.content.Context;
import android.location.Location;
import android.os.Bundle;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.ListFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.Loader;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.customer.RedeemedOffer;
import com.shoppley.android.api.customer.RedeemedOfferResponse;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;
import com.shoppley.android.utils.Utils;

public class RedeemedListFragment extends ListFragment implements
		LoaderManager.LoaderCallbacks<List<RedeemedOffer>> {

	public static class RedeemedListAdapter extends ArrayAdapter<RedeemedOffer> {
		private final LayoutInflater mInflater;

		public RedeemedListAdapter(Context context) {
			super(context, android.R.layout.simple_list_item_2);
			mInflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		}

		public void setData(List<RedeemedOffer> data) {
			clear();
			if (data != null) {
				for (RedeemedOffer offerEntry : data) {
					add(offerEntry);
				}
			}
		}

		/**
		 * Populate new items in the list.
		 */
		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			View view;

			if (convertView == null) {
				view = mInflater.inflate(R.layout.redeem_list_item, parent,
						false);
			} else {
				view = convertView;
			}

			RedeemedOffer item = getItem(position);
			// ((ImageView) view.findViewById(R.id.icon)).setImageDrawable(item
			// .getIcon());
			WebImageView imgView = ((WebImageView) view.findViewById(R.id.icon));
			imgView.setImageUrl(item.img);
			imgView.loadImage();

			((TextView) view.findViewById(R.id.txtRedeem))
					.setText(Utils.secEpochToLocaleString(Long
							.parseLong(item.redeemed_time)));
			((TextView) view.findViewById(R.id.txtNm)).setText(item.name);
			((TextView) view.findViewById(R.id.txtMrchntNm))
					.setText(item.merchant_name);
			((TextView) view.findViewById(R.id.txtDsc))
					.setText(item.description);
			return view;
		}
	}

	// This is the Adapter being used to display the list's data.
	RedeemedListAdapter mAdapter;

	// If non-null, this is the current filter the user has provided.
	String mCurFilter;

	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);

		// Give some text to display if there is no data. In a real
		// application this would come from a resource.
		// setEmptyText(getString(R.string.no_offers));
		setEmptyText("No offers");

		// We have a menu item to show in action bar.
		// setHasOptionsMenu(true);

		// Create an empty adapter we will use to display the loaded data.
		mAdapter = new RedeemedListAdapter(getActivity());
		setListAdapter(mAdapter);

		// Start out with a progress indicator.
		setListShown(false);

		// Prepare the loader. Either re-connect with an existing one,
		// or start a new one.
		getLoaderManager().initLoader(0, null, this);
	}

	@Override
	public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
		// Place an action bar item for searching.
		// MenuItem item = menu.add("Search");
		// item.setIcon(android.R.drawable.ic_menu_search);
		// item.setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM);
		// SearchView sv = new SearchView(getActivity());
		// sv.setOnQueryTextListener(this);
		// item.setActionView(sv);
	}

	public boolean onQueryTextChange(String newText) {
		// Called when the action bar search text has changed. Since this
		// is a simple array adapter, we can just have it do the filtering.
		mCurFilter = !TextUtils.isEmpty(newText) ? newText : null;
		mAdapter.getFilter().filter(mCurFilter);
		return true;
	}

	public boolean onQueryTextSubmit(String query) {
		// Don't care about this.
		return true;
	}

	@Override
	public void onListItemClick(ListView l, View v, int position, long id) {
		// Log.i("LoaderCustom", "Item clicked: " + id);

		RedeemedOffer item = (RedeemedOffer) l.getItemAtPosition(position);
		FragmentTransaction ft = getActivity().getSupportFragmentManager()
				.beginTransaction();
		ft.hide(((ShoppleyActivity) getActivity()).shoppleyFragment);
		ft.add(R.id.simple_fragment, new RedeemedFragment(item));
		ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
		ft.addToBackStack(null);
		ft.commit();
		// Intent intent = new Intent();
		// intent.setClass(getActivity(), RedeemedActivity.class);
		// startActivity(intent);
	}

	public Loader<List<RedeemedOffer>> onCreateLoader(int id, Bundle args) {
		// This is called when a new Loader needs to be created. This
		// sample only has one Loader with no arguments, so it is simple.
		return new OfferListLoader<RedeemedOffer>(getActivity(),
				new OfferListLoader.Callback<RedeemedOffer>() {
					public List<RedeemedOffer> execute() {
						ShoppleyApplication app = (ShoppleyApplication) getActivity()
								.getApplication();
						ShoppleyCustomerAPI api = app.getAPI();
						Location loc = app.getLocation();
						RedeemedOfferResponse redeemedOffer = null;
						if (loc != null) {
							redeemedOffer = api.customerShowRedeemedOffers(
									loc.getLatitude(), loc.getLongitude());
							if (redeemedOffer != null) {
								// for (RedeemedOffer offer:
								// redeemedOffer.offers){
								// offer.loadIcon();
								// }
								return redeemedOffer.offers;
							}
						} else {
							// TODO Cannot obtain location
							// Will try again or use user's zipcode
						}
						return null;
					}
				});
	}

	public void onLoadFinished(Loader<List<RedeemedOffer>> loader,
			List<RedeemedOffer> data) {
		// Set the new data in the adapter.
		mAdapter.setData(data);

		// The list should now be shown.
		if (isResumed()) {
			setListShown(true);
		} else {
			setListShownNoAnimation(true);
		}
	}

	public void onLoaderReset(Loader<List<RedeemedOffer>> loader) {
		// Clear the data in the adapter.
		mAdapter.setData(null);
	}

}