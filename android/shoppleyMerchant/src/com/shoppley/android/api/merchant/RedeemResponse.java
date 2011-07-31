package com.shoppley.android.api.merchant;

import com.google.gson.annotations.SerializedName;

public class RedeemResponse {
	@SerializedName("offer_code")
	public RedeemedOffer offer_code;
	@SerializedName("result")
	public String result;
	@SerializedName("result_msg")
	public String result_msg;
}