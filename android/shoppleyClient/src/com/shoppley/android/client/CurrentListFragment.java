package com.shoppley.android.client;

import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

import android.content.Context;
import android.location.Location;
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
import android.widget.Toast;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.customer.CurrentOffer;
import com.shoppley.android.api.customer.CurrentOfferResponse;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;

public class CurrentListFragment extends ListFragment implements
		LoaderManager.LoaderCallbacks<List<CurrentOffer>> {

	public static class CurrentListAdapter extends ArrayAdapter<CurrentOffer> {
		private final LayoutInflater mInflater;

		public CurrentListAdapter(Context context) {
			super(context, android.R.layout.simple_list_item_2);
			mInflater = (LayoutInflater) context
					.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
		}

		public void addData(List<CurrentOffer> data) {
			if (data != null) {
				for (CurrentOffer offerEntry : data) {
					add(offerEntry);
				}
			}
		}

		public void setData(List<CurrentOffer> data) {
			clear();
			if (data != null) {
				for (CurrentOffer offerEntry : data) {
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
						.inflate(R.layout.deal_list_item, parent, false);
			} else {
				view = convertView;
			}

			CurrentOffer item = getItem(position);
			// ((ImageView) view.findViewById(R.id.icon)).setImageDrawable(item
			// .getIcon());
			WebImageView imgView = ((WebImageView) view.findViewById(R.id.icon));
			imgView.setImageUrl(item.img);
			imgView.loadImage();
			((TextView) view.findViewById(R.id.txtNm)).setText(item.name);
			((TextView) view.findViewById(R.id.txtXprs)).setText(item.expires);
			((TextView) view.findViewById(R.id.txtMrchntNm))
					.setText(item.merchant_name);
			((TextView) view.findViewById(R.id.txtDsc))
					.setText(item.description);
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

	//
	// void addFragmentToStack() {
	// // mStackLevel++;
	//
	// // Instantiate a new fragment.
	// Fragment newFragment = CountingFragment.newInstance(1);
	//
	// // Add the fragment to the activity, pushing this transaction
	// // on to the back stack.
	// FragmentTransaction ft = getFragmentManager().beginTransaction();
	// ft.replace(R.id.simple_fragment, newFragment);
	// ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
	// ft.addToBackStack(null);
	// ft.commit();
	// }

	// public static class CountingFragment extends Fragment {
	// int mNum;
	//
	// /**
	// * Create a new instance of CountingFragment, providing "num" as an
	// * argument.
	// */
	// static CountingFragment newInstance(int num) {
	// CountingFragment f = new CountingFragment();
	//
	// // Supply num input as an argument.
	// Bundle args = new Bundle();
	// args.putInt("num", num);
	// f.setArguments(args);
	//
	// return f;
	// }
	//
	// /**
	// * When creating, retrieve this instance's number from its arguments.
	// */
	// @Override
	// public void onCreate(Bundle savedInstanceState) {
	// super.onCreate(savedInstanceState);
	// mNum = getArguments() != null ? getArguments().getInt("num") : 1;
	// }
	//
	// /**
	// * The Fragment's UI is just a simple text view showing its instance
	// * number.
	// */
	// @Override
	// public View onCreateView(LayoutInflater inflater, ViewGroup container,
	// Bundle savedInstanceState) {
	// View v = inflater.inflate(R.layout.hello_world, container, false);
	// View tv = v.findViewById(R.id.text);
	// ((TextView) tv).setText("Fragment #" + mNum);
	// tv.setBackgroundDrawable(getResources().getDrawable(
	// android.R.drawable.gallery_thumb));
	// return v;
	// }
	// }

	@Override
	public void onListItemClick(ListView l, View v, int position, long id) {
		// Log.i("LoaderCustom", "Item clicked: " + id);
		// addFragmentToStack();

		CurrentOffer item = (CurrentOffer) l.getItemAtPosition(position);
		FragmentTransaction ft = getActivity().getSupportFragmentManager()
				.beginTransaction();
		ft.hide(((ShoppleyActivity) getActivity()).shoppleyFragment);
		ft.add(R.id.simple_fragment, new CurrentFragment(item));
		ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
		ft.addToBackStack(null);
		ft.commit();
		// Intent intent = new Intent();
		// intent.putExtra(Offer.CURRENT_OFFER,item);
		// intent.setClass(getActivity(), CurrentActivity.class);
		// startActivity(intent);
	}

	public Loader<List<CurrentOffer>> onCreateLoader(int id, Bundle args) {
		// This is called when a new Loader needs to be created. This
		// sample only has one Loader with no arguments, so it is simple.
		return new OfferListLoader<CurrentOffer>(getActivity(),
				new OfferListLoader.Callback<CurrentOffer>() {
					public List<CurrentOffer> execute() {
						// Log.d("Loading: ", "start");
						ShoppleyApplication app = (ShoppleyApplication) getActivity()
								.getApplication();
						ShoppleyCustomerAPI api = app.getAPI();
						Location loc = app.getLocation();
						CurrentOfferResponse currentoffer = null;
						if (loc != null) {
							currentoffer = api.customerShowOffers(
									loc.getLatitude(), loc.getLongitude());
							if (currentoffer != null) {
								// for (Offer offer:
								// currentoffer.offers) {
								// offer.loadIcon();
								// }
								// Log.d("Loading: ", "end");
								return currentoffer.offers;
							}
						} else {
							// TODO Cannot obtain location
							// Will try again or use user's zipcode
							handler.post(new MyRunnable() {
								@Override
								protected void runItem() {
									Toast.makeText(
											getActivity(),
											"Cannot find your location. Please check your location settings.",
											1000).show();
								}
							});
							handler.postDelayed(new MyRunnable() {
								@Override
								protected void runItem() {
									getLoaderManager().restartLoader(0, null,
											CurrentListFragment.this);
								}
							}, 3000);

						}
						// Log.d("Loading: ", "end");
						return null;
					}
				});
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		View v = super.onCreateView(inflater, container, savedInstanceState);
		ListView lv = (ListView) v.findViewById(android.R.id.list);
		// TODO to implement incremental loading
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
		// ADD FOOTER VIEW
		// lv.addFooterView(lv);
		
		handler = new Handler();
		return v;
	}

	public void onLoadFinished(Loader<List<CurrentOffer>> loader,
			List<CurrentOffer> data) {
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

	public void onLoaderReset(Loader<List<CurrentOffer>> loader) {
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
