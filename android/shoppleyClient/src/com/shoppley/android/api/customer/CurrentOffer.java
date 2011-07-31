package com.shoppley.android.api.customer;

import android.graphics.drawable.Drawable;

import com.google.gson.annotations.SerializedName;
import com.shoppley.android.utils.Utils;

public class CurrentOffer {
	@SerializedName("offer_code_id")
	public String offer_code_id;
	@SerializedName("description")
	public String description;
	@SerializedName("img")
	public String img;
	@SerializedName("address1")
	public String address1;
	@SerializedName("offer_id")
	public String offer_id;
	@SerializedName("expires")
	public String expires;
	@SerializedName("lon")
	public String lon;
	@SerializedName("name")
	public String name;
	@SerializedName("phone")
	public String phone;
	@SerializedName("code")
	public String code;
	@SerializedName("expires_time")
	public String expires_time;
	@SerializedName("citystatezip")
	public String citystatezip;
	@SerializedName("lat")
	public String lat;
	@SerializedName("banner")
	public String banner;
	@SerializedName("merchant_name")
	public String merchant_name;
	@SerializedName("rating")
	public String rating;

	private Drawable iconDrawable;
	private Drawable bannerDrawable;
	private Drawable mapDrawable;

	public void loadIcon() {
		iconDrawable = Utils.loadDrawableFromURL(img);
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