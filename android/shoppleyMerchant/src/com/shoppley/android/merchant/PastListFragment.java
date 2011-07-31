package com.shoppley.android.merchant;

import java.text.NumberFormat;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
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
import android.widget.AbsListView;
import android.widget.AbsListView.OnScrollListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.merchant.Offer;
import com.shoppley.android.api.merchant.PastResponse;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.utils.Utils;

public class PastListFragment extends ListFragment implements
		LoaderManager.LoaderCallbacks<List<Offer>> {

	public static class CurrentListAdapter extends ArrayAdapter<Offer> {
		private final LayoutInflater mInflater;

		public CurrentListAdapter(Context context) {
			super(context, android.R.layout.simple_list_item_2);
			mInflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		}

		public void addData(List<Offer> data) {
			if (data != null) {
				for (Offer offerEntry : data) {
					add(offerEntry);
				}
			}
		}

		public void setData(List<Offer> data) {
			clear();
			if (data != null) {
				for (Offer offerEntry : data) {
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
				view = mInflater
						.inflate(R.layout.past_list_item, parent, false);
			} else {
				view = convertView;
			}

			Offer item = getItem(position);
			// ((ImageView) view.findViewById(R.id.icon)).setImageDrawable(item
			// .getIcon());
			WebImageView imgView = ((WebImageView) view.findViewById(R.id.icon));
			imgView.setImageUrl(item.img);
			imgView.loadImage();
			((TextView) view.findViewById(R.id.txtNm)).setText(item.title);
			((TextView) view.findViewById(R.id.txtXprs)).setText(Utils
					.secEpochToLocaleString(Long.parseLong(item.expires)));
			// ((TextView) view.findViewById(R.id.txtMrchntNm))
			// .setText(item.merchant_name);
			((TextView) view.findViewById(R.id.txtReached))
					.setText(item.redeemed
							+ "("
							+ NumberFormat.getPercentInstance().format(
									Float.parseFloat(item.redeem_rate) / 100)
							+ ")");
			return view;
		}
	}

	private Handler handler;
	// This is the Adapter being used to display the list's data.
	private CurrentListAdapter mAdapter;

	// If non-null, this is the current filter the user has provided.
	private String mCurFilter;

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
		mAdapter = new CurrentListAdapter(getActivity());
		setListAdapter(mAdapter);

		// Start out with a progress indicator.
		setListShown(false);

		// Prepare the loader. Either re-connect with an existing one,
		// or start a new one.
		// for (int i = 0; i < 30; i++) {
		getLoaderManager().initLoader(0, null, this);
		// }
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
		// addFragmentToStack();

		// TODO What to do when click
		Offer item = (Offer) l.getItemAtPosition(position);
		FragmentTransaction ft = getActivity().getSupportFragmentManager()
				.beginTransaction();
		ft.hide(((MerchantActivity) getActivity()).shoppleyFragment);
		ft.add(R.id.simple_fragment, new PastFragment(item));
		ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
		ft.addToBackStack(null);
		ft.commit();
		// Intent intent = new Intent();
		// intent.putExtra(Offer.CURRENT_OFFER, item);
		// intent.setClass(getActivity(), CurrentActivity.class);
		// startActivity(intent);
	}

	public Loader<List<Offer>> onCreateLoader(int id, Bundle args) {
		// This is called when a new Loader needs to be created. This
		// sample only has one Loader with no arguments, so it is simple.
		return new OfferListLoader<Offer>(getActivity(),
				new OfferListLoader.Callback<Offer>() {
					public List<Offer> execute() {
						// Log.d("Loading: ", "start");
						MerchantApplication app = (MerchantApplication) getActivity()
								.getApplication();
						ShoppleyMerchantAPI api = app.getAPI();
						PastResponse offer = null;
						offer = api
								.merchantPastOffer(ShoppleyMerchantAPI.PAST_0);
						if (offer != null && offer.offers != null
								&& offer.offers.size() > 0) {
							return offer.offers;
						}
						return null;
					}
				});
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = super.onCreateView(inflater, container, savedInstanceState);
		ListView lv = (ListView) v.findViewById(android.R.id.list);

		// TODO: incremental loading
		lv.setOnScrollListener(new OnScrollListener() {

			public void onScrollStateChanged(AbsListView view, int scrollState) {
				// TODO Auto-generated method stub

			}

			public void onScroll(AbsListView view, int firstVisibleItem,
					int visibleItemCount, int totalItemCount) {
				// TODO Auto-generated method stub
				// Fire new loader
			}
		});

		handler = new Handler();
		return v;
	}

	public void onLoadFinished(Loader<List<Offer>> loader, List<Offer> data) {
		// Set the new data in the adapter.
		mAdapter.setData(data);

		// The list should now be shown.
		if (isResumed()) {
			setListShown(true);
		} else {
			try {
				setListShownNoAnimation(true);
			} catch (IllegalStateException e) {
				handler.postDelayed(new MyRunnable() {
					@Override
					protected void runItem() {
						if (isResumed()) {
							setListShownNoAnimation(true);
						} else {
							handler.postDelayed(this, 500);
						}
					}
				}, 500);
			}
		}
	}

	public void onLoaderReset(Loader<List<Offer>> loader) {
		// Clear the data in the adapter.
		mAdapter.setData(null);
	}

	public abstract class MyRunnable implements Runnable {
		public void run() {
			if (!exiting.get()) {
				runItem();
			}
		}

		protected abstract void runItem();
	}

	private AtomicBoolean exiting = new AtomicBoolean();

	@Override
	public void onDestroy() {
		super.onDestroy();
		exiting.set(true);
	};

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		exiting.set(false);
	};
}
