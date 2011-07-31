package com.shoppley.android.client;

import java.text.NumberFormat;
import java.util.Date;

import android.app.ProgressDialog;
import android.content.Context;
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
import android.widget.RatingBar;
import android.widget.RatingBar.OnRatingBarChangeListener;
import android.widget.TextView;
import android.widget.Toast;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.customer.RateOfferResponse;
import com.shoppley.android.api.customer.RedeemedOffer;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;
import com.shoppley.android.utils.Utils;

public class RedeemedFragment extends Fragment {

	private WebImageView img;
	private ImageView imgMap;
	private ImageView imgBanner;
	private Button btnDirection;
	private Button btnFeedback;
	private Button btnForward;
	private TextView txtTitle;
	private TextView txtMerchant;
	private TextView txtDesc;
	private TextView txtRedeemOn;
	private TextView txtCost;
	private TextView txtAddress;
	private TextView txtPhone;
	private ImageButton btnPhone;
	private Button btnRate;
	private RatingBar ratingBar;

	private RedeemedOffer redeemedOffer = null;
	private RatingBar ratingBarIndicator;

	public RedeemedFragment(RedeemedOffer offer) {
		redeemedOffer = offer;
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = inflater.inflate(R.layout.redeemed_detail, container, false);
		img = (WebImageView) v.findViewById(R.id.img);
		imgMap = (ImageView) v.findViewById(R.id.imgMap);
		imgBanner = (ImageView) v.findViewById(R.id.imgBanner);
		btnDirection = (Button) v.findViewById(R.id.btnDirection);
		btnFeedback = (Button) v.findViewById(R.id.btnFeedback);
		btnForward = (Button) v.findViewById(R.id.btnForward);
		txtTitle = (TextView) v.findViewById(R.id.txtTitle);
		txtMerchant = (TextView) v.findViewById(R.id.txtMerchant);
		txtDesc = (TextView) v.findViewById(R.id.txtDesc);
		txtRedeemOn = (TextView) v.findViewById(R.id.txtRedeemOn);
		txtCost = (TextView) v.findViewById(R.id.txtCost);
		txtAddress = (TextView) v.findViewById(R.id.txtAddress);
		txtPhone = (TextView) v.findViewById(R.id.txtPhone);
		btnPhone = (ImageButton) v.findViewById(R.id.imgBtnPhone);
		ratingBar = (RatingBar) v.findViewById(R.id.ratingBar);
		btnRate = (Button) v.findViewById(R.id.btnRate);

		btnRate.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// TODO Auto-generated method stub
				ratingBar.setVisibility(View.VISIBLE);
				btnRate.setVisibility(View.GONE);
			}
		});

		ratingBar.setStepSize(1.0f);
		ratingBar.setRating(Float.parseFloat(redeemedOffer.rating));
		ratingBar.setOnRatingBarChangeListener(new OnRatingBarChangeListener() {
			public void onRatingChanged(final RatingBar ratingBar,
					float rating, boolean fromUser) {
				// TODO Auto-generated method stub
				ShoppleyApplication app = (ShoppleyApplication) getActivity()
						.getApplication();
				final ShoppleyCustomerAPI api = app.getAPI();

				final ProgressDialog dialog = Utils.showLoading(getActivity(),
						"Sending rating request...");
				BetterAsyncTask<Void, Void, RateOfferResponse> task = new BetterAsyncTask<Void, Void, RateOfferResponse>(
						getActivity()) {
					@Override
					protected void after(Context arg0, RateOfferResponse arg1) {
						dialog.hide();
						if (arg1 != null && arg1.result.equals("1")) {
							Toast.makeText(getActivity(),
									getString(R.string.successfully_rated), 500)
									.show();
						} else {
							Toast.makeText(getActivity(),
									getString(R.string.failed_to_rate), 500)
									.show();
						}
					}

					@Override
					protected void handleError(Context arg0, Exception arg1) {
						dialog.hide();
						Toast.makeText(getActivity(),
								getString(R.string.failed_to_rate), 500).show();
					}
				};
				task.setCallable(new BetterAsyncTaskCallable<Void, Void, RateOfferResponse>() {

					public RateOfferResponse call(
							BetterAsyncTask<Void, Void, RateOfferResponse> arg0)
							throws Exception {
						return api.customerRateOffer(
								redeemedOffer.offer_code_id, ""
										+ (int) ratingBar.getRating());
					}
				});

				task.execute();

			}
		});

		// img.setImageDrawable(redeemedOffer.getIcon());
		img.setImageUrl(redeemedOffer.img);
		img.loadImage();

		if (redeemedOffer.getBanner() == null) {
			// Load images in background
			new AsyncTask<Void, Void, Void>() {

				@Override
				protected Void doInBackground(Void... params) {
					// redeemedOffer
					// .loadMap("http://maps.googleapis.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&size=256x256&maptype=roadmap&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318&markers=color:red%7Ccolor:red%7Clabel:C%7C40.718217,-73.998284&sensor=false");
					redeemedOffer.loadBanner();
					return null;
				}

				protected void onPostExecute(Void result) {
					// imgMap.setImageDrawable(redeemedOffer.getMap());
					imgBanner.setImageDrawable(redeemedOffer.getBanner());
				};
			}.execute();
		} else {
			imgBanner.setImageDrawable(redeemedOffer.getBanner());
		}

		btnDirection.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// geo:latitude,longitude
				// geo:latitude,longitude?z=zoom
				// geo:0,0?q=my+street+address
				// geo:0,0?q=business+near+city
				try {
					Intent intent = new Intent(Intent.ACTION_VIEW);
					intent.setData(Uri.parse("geo:0,0?q=" + redeemedOffer.lat
							+ "," + redeemedOffer.lon + "("
							+ redeemedOffer.merchant_name + ")"));
					startActivity(intent);
				} catch (Exception e) {
					Log.e(getClass().toString(), "Failed to invoke call");
				}
			}
		});
		Date today = new Date();
		if (Long.parseLong(redeemedOffer.expires_time) > today.getTime()) {
			btnForward.setVisibility(View.VISIBLE);
			btnForward.setOnClickListener(new OnClickListener() {
				public void onClick(View v) {
					// String subject = redeemedOffer.name + " from"
					// + redeemedOffer.merchant_name;
					// String body = "Address: " + redeemedOffer.address1
					// + " Redeem code: " + redeemedOffer.code;
					// Utils.forwardText(getActivity(), subject, body,
					// new Callback<Intent>() {
					// public void call(Intent... param) {
					// startActivity(param[0]);
					// }
					// });
					// Instantiate a new fragment.
					Fragment newFragment = new ForwardFragment(
							redeemedOffer.code, redeemedOffer.name);

					// Add the fragment to the activity, pushing this
					// transaction
					// on to the back stack.
					FragmentTransaction ft = getFragmentManager()
							.beginTransaction();
					ft.hide(RedeemedFragment.this);
					ft.add(R.id.simple_fragment, newFragment);
					ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
					ft.addToBackStack(null);
					ft.commit();
				}
			});
		} else {
			btnForward.setVisibility(View.GONE);
		}

		btnFeedback.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// Instantiate a new fragment.
				Fragment newFragment = new FeedbackFragment(redeemedOffer);

				// Add the fragment to the activity, pushing this transaction
				// on to the back stack.
				FragmentTransaction ft = getFragmentManager()
						.beginTransaction();
				ft.hide(RedeemedFragment.this);
				ft.add(R.id.simple_fragment, newFragment);
				ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
				ft.addToBackStack(null);
				ft.commit();
			}
		});

		txtTitle.setText(redeemedOffer.name);
		txtMerchant.setText(redeemedOffer.merchant_name);
		txtDesc.setText(redeemedOffer.description);

		txtRedeemOn.setText(Utils.secEpochToLocaleString(Long
				.parseLong(redeemedOffer.redeemed_time)));
		NumberFormat nf = NumberFormat.getCurrencyInstance();
		txtCost.setText(nf.format(Double.parseDouble(redeemedOffer.txn_amount)));

		txtAddress.setText(redeemedOffer.address1 + " "
				+ redeemedOffer.citystatezip);
		txtPhone.setText(redeemedOffer.phone);

		btnPhone.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				try {
					Intent intent = new Intent(Intent.ACTION_CALL);
					intent.setData(Uri.parse("tel:" + redeemedOffer.phone));
					startActivity(intent);
				} catch (Exception e) {
					Log.e(getClass().toString(), "Failed to invoke call");
				}
			}
		});

		ratingBarIndicator = (RatingBar) v
				.findViewById(R.id.ratingBarIndicator);
		ratingBarIndicator.setRating(Float.parseFloat(redeemedOffer.rating));

		return v;
	}
}
