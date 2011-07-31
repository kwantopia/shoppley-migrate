package com.shoppley.android.api.merchant;

import com.google.gson.annotations.SerializedName;

public class ValueOffer {
	@SerializedName("received")
	public String received;
	@SerializedName("redeem_rate")
	public String redeem_rate;
	@SerializedName("description")
	public String description;
	@SerializedName("img")
	public String img;
	@SerializedName("title")
	public String title;
	@SerializedName("offer_id")
	public String offer_id;
	@SerializedName("expires")
	public String expires;
	@SerializedName("redistributable")
	public String redistributable;
	@SerializedName("amount")
	public String amount;
	@SerializedName("redeemed")
	public String redeemed;
	@SerializedName("redistribute_processing")
	public String redistribute_processing;
	@SerializedName("duration")
	public String duration;
	@SerializedName("unit")
	public String unit;
	@SerializedName("is_processing")
	public String is_processing;
}