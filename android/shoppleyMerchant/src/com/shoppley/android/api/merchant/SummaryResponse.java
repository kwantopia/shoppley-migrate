package com.shoppley.android.api.merchant;

import com.google.gson.annotations.SerializedName;

public class SummaryResponse {
	@SerializedName("total_forwarded")
	public String total_forwarded;
	@SerializedName("total_redeemed")
	public String total_redeemed;
	@SerializedName("redeem_rate")
	public String redeem_rate;
	@SerializedName("result_msg")
	public String result_msg;
	@SerializedName("total_received")
	public String total_received;
	@SerializedName("result")
	public String result;
	@SerializedName("num_offers")
	public String num_offers;
}