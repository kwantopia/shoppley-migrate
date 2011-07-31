package com.shoppley.android.api.customer;

import android.graphics.drawable.Drawable;
import android.util.Log;

import com.google.gson.annotations.SerializedName;
import com.shoppley.android.utils.Utils;

public class RedeemedOffer {
	@SerializedName("rating")
	public String rating;
	@SerializedName("offer_code_id")
	public String offer_code_id;
	@SerializedName("name")
	public String name;
	@SerializedName("img")
	public String img;
	@SerializedName("redeemed")
	public String redeemed;
	@SerializedName("redeemed_time")
	public String redeemed_time;
	@SerializedName("address1")
	public String address1;
	@SerializedName("offer_id")
	public String offer_id;
	@SerializedName("description")
	public String description;
	@SerializedName("lon")
	public String lon;
	@SerializedName("banner")
	public String banner;
	@SerializedName("phone")
	public String phone;
	@SerializedName("citystatezip")
	public String citystatezip;
	@SerializedName("lat")
	public String lat;
	@SerializedName("merchant_name")
	public String merchant_name;
	@SerializedName("txn_amount")
	public String txn_amount;
	@SerializedName("feedback")
	public String feedback;
	@SerializedName("can_forward")
	public String can_forward;
	@SerializedName("code")
	public String code;
	@SerializedName("expires_time")
	public String expires_time;
	
	private Drawable iconDrawable;
	private Drawable bannerDrawable;
	private Drawable mapDrawable;

	public void loadIcon() {
		iconDrawable = Utils.loadDrawableFromURL(img);
		Log.d("XXXXiconDrawable", iconDrawable.toString());
	}

	public void loadBanner() {
		bannerDrawable = Utils.loadDrawableFromURL(banner);
	}

	public void loadMap(String url) {
		mapDrawable = Utils.loadDrawableFromURL(url);
	}

	public Drawable getIcon() {
		return iconDrawable;
	}

	public Drawable getBanner() {
		return bannerDrawable;
	}

	public Drawable getMap() {
		return mapDrawable;
	}
}