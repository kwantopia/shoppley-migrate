package com.shoppley.android.api.merchant;

import java.util.List;

import com.google.gson.annotations.SerializedName;

public class ActiveResponse {
	@SerializedName("offers")
	public List<Offer> offers;
	@SerializedName("result")
	public String result;
	@SerializedName("result_msg")
	public String result_msg;
}