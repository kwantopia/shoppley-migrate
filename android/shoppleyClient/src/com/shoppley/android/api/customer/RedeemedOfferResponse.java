package com.shoppley.android.api.customer;

import java.util.List;

import com.google.gson.annotations.SerializedName;

public class RedeemedOfferResponse {
	@SerializedName("offers")
	public List<RedeemedOffer> offers;
	@SerializedName("num_offers")
	public String num_offers;
	@SerializedName("result")
	public String result;
	@SerializedName("result_msg")
	public String result_msg;
}