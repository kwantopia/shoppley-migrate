package com.shoppley.android.merchant;

import java.text.NumberFormat;
import java.util.Date;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.merchant.Offer;
import com.shoppley.android.utils.Utils;

public class PastFragment extends Fragment {
	private TextView txtTitle;
	private WebImageView img;
	private TextView txtDesc;
	private TextView txtExpires;
	private TextView txtSendto;
	private TextView txtRedeem;
	private TextView txtPercentage;
	private Offer offer;
	private Button btnRestart;

	public PastFragment(Offer offer) {
		this.offer = offer;
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

	}

	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);

	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = inflater.inflate(R.layout.past_detail, container, false);
		txtTitle = (TextView) v.findViewById(R.id.txtTitle);
		img = (WebImageView) v.findViewById(R.id.img);
		txtDesc = (TextView) v.findViewById(R.id.txtDesc);
		txtExpires = (TextView) v.findViewById(R.id.txtExpires);
		txtSendto = (TextView) v.findViewById(R.id.txtSendTo);
		txtRedeem = (TextView) v.findViewById(R.id.txtRedeem);
		txtPercentage = (TextView) v.findViewById(R.id.txtPercentage);
		btnRestart = (Button) v.findViewById(R.id.btnRestart);

		txtTitle.setText(offer.title);
		img.setImageUrl(offer.img);
		img.loadImage();
		txtDesc.setText(offer.description);
		txtExpires.setText(Utils.secEpochToLocaleString(Long
				.parseLong(offer.expires)));
		txtSendto.setText(offer.received);
		txtRedeem.setText(offer.redeemed);
		txtPercentage.setText(NumberFormat.getPercentInstance().format(
				Float.parseFloat(offer.redeem_rate) / 100));

		btnRestart.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				FragmentTransaction ft = getActivity()
						.getSupportFragmentManager().beginTransaction();
				ft.hide(((MerchantActivity) getActivity()).shoppleyFragment);
				ft.add(R.id.simple_fragment, new NewOfferFragment(offer));
				ft.setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN);
				ft.addToBackStack(null);
				ft.commit();
			}
		});
		return v;
	}
}
