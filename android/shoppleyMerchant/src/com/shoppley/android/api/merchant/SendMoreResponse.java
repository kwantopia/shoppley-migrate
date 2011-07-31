package com.shoppley.android.api.merchant;

import com.google.gson.annotations.SerializedName;

public class SendMoreResponse {
	@SerializedName("result_msg")
	public String result_msg;
	@SerializedName("result")
	public String result;
	@SerializedName("offer")
	public ValueOffer offer;
}