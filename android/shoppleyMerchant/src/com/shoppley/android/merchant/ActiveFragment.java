package com.shoppley.android.merchant;

import java.text.NumberFormat;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.github.droidfu.widgets.WebImageView;
import com.shoppley.android.api.merchant.Offer;
import com.shoppley.android.utils.Utils;

public class ActiveFragment extends Fragment {
	private TextView txtTitle;
	private WebImageView img;
	private TextView txtDesc;
	private TextView txtExpires;
	private TextView txtSendto;
	private TextView txtRedeem;
	private TextView txtPercentage;
	private Offer offer;

	/**
	 * Create a new instance of DetailsFragment, initialized to show the text at
	 * 'index'.
	 * 
	 * @param object
	 */

	public ActiveFragment(Offer offer) {
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
		View v = inflater.inflate(R.layout.active_detail, container, false);
		txtTitle = (TextView) v.findViewById(R.id.txtTitle);
		img = (WebImageView) v.findViewById(R.id.img);
		txtDesc = (TextView) v.findViewById(R.id.txtDesc);
		txtExpires = (TextView) v.findViewById(R.id.txtExpires);
		txtSendto = (TextView) v.findViewById(R.id.txtSendTo);
		txtRedeem = (TextView) v.findViewById(R.id.txtRedeem);
		txtPercentage = (TextView) v.findViewById(R.id.txtPercentage);

		txtTitle.setText(offer.title);
		img.setImageUrl(offer.img);
		img.loadImage();
		txtDesc.setText(offer.description);
		String str = Utils.getExpiresIn(Long
				.parseLong(offer.expires));
		if (str != "")
			txtExpires.setText(str);
		else
			txtExpires.setText("expired");
		txtSendto.setText(offer.received);
		txtRedeem.setText(offer.redeemed);
		txtPercentage.setText(NumberFormat.getPercentInstance().format(
				Float.parseFloat(offer.redeem_rate) / 100));

		return v;
	}
}
