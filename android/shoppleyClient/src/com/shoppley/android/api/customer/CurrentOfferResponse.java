package com.shoppley.android.api.customer;

import java.util.List;

import com.google.gson.annotations.SerializedName;

public class CurrentOfferResponse {
	@SerializedName("offers")
	public List<CurrentOffer> offers;
	@SerializedName("num_offers")
	public String num_offers;
	@SerializedName("result")
	public String result;
	@SerializedName("result_msg")
	public String result_msg;
}