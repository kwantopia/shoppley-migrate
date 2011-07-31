package com.shoppley.android.api.customer;

import com.google.gson.annotations.SerializedName;

public class OffercodeResponse{
	@SerializedName("offer")
	public Offercode offer;
	@SerializedName("result")
	public String result;
	@SerializedName("result_msg")
	public String result_msg;
}
