package com.shoppley.android.client;

import android.content.Intent;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.RatingBar;
import android.widget.TextView;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.customer.CurrentOffer;
import com.shoppley.android.api.customer.OffercodeResponse;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;
import com.shoppley.android.utils.Utils;

public class CurrentFragment extends Fragment {
	/**
	 * Create a new instance of DetailsFragment, initialized to show the text at
	 * 'index'.
	 * 
	 * @param object
	 */
	private WebImageView img;
	private ImageView imgMap;
	private ImageView imgBanner;
	private Button btnDirection;
	private Button btnForward;
	private TextView txtTitle;
	private TextView txtMerchant;
	private TextView txtDesc;
	private TextView txtExpires;
	private TextView txtRedeem;
	private TextView txtAddress;
	private TextView txtPhone;
	private ImageButton btnPhone;
	private ProgressBar progressBar;

	public CurrentFragment(CurrentOffer offer) {
		currentOffer = offer;
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);

	}

	private CurrentOffer currentOffer = null;
	private RatingBar ratingBarIndicator;

	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);

		// currentOffer = (Offer)getArguments().getSerializable(
		// CurrentOffer.CURRENT_OFFER);
		// Show loading
		// ProgressDialog progressDialog = Utils.showLoading(getActivity());
		// new AsyncTask<Void, Void, OffercodeResponse>(){
		//
		// @Override
		// protected OffercodeResponse doInBackground(Void... params){
		// ShoppleyApplication app = (ShoppleyApplication) getActivity()
		// .getApplication();
		// ShoppleyCustomerAPI api = app.getAPI();
		// // getOfferid frombundle
		// return api.customerRequestCurrentOfferCode(getArguments().getString(
		// OFFER_ID_ARG));
		// }
		//
		// protected void onPostExecute(OffercodeResponse result){
		// if (progressDialog.isShowing())
		// progressDialog.hide();
		// };
		// }.execute();
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = inflater.inflate(R.layout.current_detail, container, false);
		img = (WebImageView) v.findViewById(R.id.img);
		imgMap = (ImageView) v.findViewById(R.id.imgMap);
		imgBanner = (ImageView) v.findViewById(R.id.imgBanner);
		btnDirection = (Button) v.findViewById(R.id.btnDirection);
		btnForward = (Button) v.findViewById(R.id.btnForward);
		txtTitle = (TextView) v.findViewById(R.id.txtTitle);
		txtMerchant = (TextView) v.findViewById(R.id.txtMerchant);
		txtDesc = (TextView) v.findViewById(R.id.txtDesc);
		txtExpires = (TextView) v.findViewById(R.id.txtExpires);
		txtRedeem = (TextView) v.findViewById(R.id.txtRedeem);
		txtAddress = (TextView) v.findViewById(R.id.txtAddress);
		txtPhone = (TextView) v.findViewById(R.id.txtPhone);
		btnPhone = (ImageButton) v.findViewById(R.id.imgBtnPhone);
		progressBar = (ProgressBar) v.findViewById(R.id.progressBarCode);

		img.setImageUrl(currentOffer.img);
		img.loadImage();
		// img.setImageDrawable(currentOffer.getIcon());

		if (currentOffer.getBanner() == null) {
			// Load images in background
			new AsyncTask<Void, Void, Void>() {

				@Override
				protected Void doInBackground(Void... params) {
					// currentOffer
					// .loadMap("http://maps.googleapis.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&size=256x256&maptype=roadmap&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318&markers=color:red%7Ccolor:red%7Clabel:C%7C40.718217,-73.998284&sensor=false");
					currentOffer.loadBanner();
					return null;
				}

				protected void onPostExecute(Void result) {
					// imgMap.setImageDrawable(currentOffer.getMap());
					imgBanner.setImageDrawable(currentOffer.getBanner());
				};
			}.execute();
		} else {
			imgBanner.setImageDrawable(currentOffer.getBanner());
		}

		btnDirection.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// geo:latitude,longitude
				// geo:latitude,longitude?z=zoom
				// geo:0,0?q=my+street+address
				// geo:0,0?q=business+near+city
				try {
					Intent intent = new Intent(Intent.ACTION_VIEW);
					intent.setData(Uri.parse("geo:0,0?q=" + currentOffer.lat
							+ "," + currentOffer.lon + "("
							+ currentOffer.merchant_name + ")"));
					startActivity(intent);
				} catch (Exception e) {
					Log.e(getClass().toString(), "Failed to invoke call");
				}
			}
		});

		btnForward.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// String subject = currentOffer.name + " from"
				// + currentOffer.merchant_name;
				// String body = subject + ". Address: " +
				// currentOffer.address1
				// + ". Redeem code: " + currentOffer.code;
				// Utils.forwardText(getActivity(), subject, body,
				// new Callback<Intent>() {
				// public void call(Intent... param) {
				// startActivity(param[0]);
				// }
				// });
				// Instantiate a new fragment.
				Fragment newFragment = new ForwardFragment(currentOffer.code,
						currentOffer.name);

				// Add the fragment to the activity, pushing this transaction
				// on to the back stack.
				FragmentTransaction ft = getFragmentManager()
						.beginTransaction();
				ft.hide(CurrentFragment.this);
				ft.add(R.id.simple_fragment, newFragment);
				ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
				ft.addToBackStack(null);
				ft.commit();
			}
		});

		txtTitle.setText(currentOffer.name);
		txtMerchant.setText(currentOffer.merchant_name);
		txtDesc.setText(currentOffer.description);
		txtExpires.setText(Utils.secEpochToLocaleString(Long
				.parseLong(currentOffer.expires_time)));
		if (currentOffer.code == null) {
			// Load offer code

			txtRedeem.setText("");
			progressBar.setVisibility(View.VISIBLE);
			new AsyncTask<Void, Void, OffercodeResponse>() {

				@Override
				protected OffercodeResponse doInBackground(Void... params) {
					ShoppleyCustomerAPI api = ((ShoppleyApplication) getActivity()
							.getApplication()).getAPI();
					OffercodeResponse resp = api
							.customerRequestOfferCode(currentOffer.offer_id);
					return resp;
				}

				@Override
				protected void onPostExecute(OffercodeResponse result) {
					if (result != null && result.offer != null) {
						txtRedeem.setText(result.offer.code);
						currentOffer.code = result.offer.code;
						currentOffer.offer_code_id = result.offer.offer_code_id;
					} else {
						txtRedeem.setText(getString(R.string.none));
					}
					progressBar.setVisibility(View.GONE);
				}

			}.execute();
		} else {
			progressBar.setVisibility(View.GONE);
			txtRedeem.setText(currentOffer.code);
		}

		txtAddress.setText(currentOffer.address1 + " "
				+ currentOffer.citystatezip);
		txtPhone.setText(currentOffer.phone);

		btnPhone.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				try {
					Intent intent = new Intent(Intent.ACTION_CALL);
					intent.setData(Uri.parse("tel:" + currentOffer.phone));
					startActivity(intent);
				} catch (Exception e) {
					Log.e(getClass().toString(), "Failed to invoke call");
				}
			}
		});

		ratingBarIndicator = (RatingBar) v
				.findViewById(R.id.ratingBarIndicator);
		ratingBarIndicator.setRating(Float.parseFloat(currentOffer.rating));

		return v;
	}
}
