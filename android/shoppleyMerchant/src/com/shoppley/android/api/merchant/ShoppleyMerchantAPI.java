package com.shoppley.android.api.merchant;

import java.io.IOException;

import org.apache.http.HttpResponse;
import org.apache.http.ParseException;
import org.apache.http.util.EntityUtils;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

import com.shoppley.android.api.ShoppleyAPI;

public class ShoppleyMerchantAPI extends ShoppleyAPI {

	public RegisterResponse merchantRegister(String business, String email,
			String password, String phone, String zipcode) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("business", business);
			obj.put("email", email);
			obj.put("password", password);
			obj.put("phone", phone);
			obj.put("zipcode", zipcode);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest("/m/merchant/register/",
					obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantRegister", responseStr);
			return gson.fromJson(responseStr, RegisterResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public ActiveResponse merchantGetActiveOffers() {
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpGetRequest(
					"/m/merchant/offers/active/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantGetActiveOffers", responseStr);
			return gson.fromJson(responseStr, ActiveResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	public StartResponse merchantStartOffer(String amount, String datetime,
			String description, String duration, String title, String units) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("amount", amount);
			obj.put("datetime", datetime);
			obj.put("description", description);
			obj.put("duration", duration);
			obj.put("title", title);
			obj.put("units", units);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest("/m/merchant/offer/start/",
					obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantStartOffer", responseStr);
			return gson.fromJson(responseStr, StartResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}

	/**
	 * 
	 * @param offer_id
	 * @return result:1
	 *         "Offers were sent but not clear how many people reached."
	 *         result:0
	 *         "There were no customers that could be reached at this moment."
	 *         result:-4
	 *         "You have already redistributed this offer.  Create a new offer to reach more customers."
	 */
	public SendMoreResponse merchantSendMoreOffer(String offer_id) {
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpGetRequest(
					"/m/merchant/offer/send/more/" + offer_id + "/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantSendMoreOffer", responseStr);
			return gson.fromJson(responseStr, SendMoreResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;

	}

	public RestartResponse merchantRestartOffer(String offer_id) {
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpPostRequest(
					"/m/merchant/offer/restart/" + offer_id + "/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantGetActiveOffers", responseStr);
			return gson.fromJson(responseStr, RestartResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;

	}

	public RedeemResponse merchantRedeemOffer(String amount, String code) {
		JSONObject obj = new JSONObject();
		try {
			obj.put("amount", amount);
			obj.put("code", code);
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		try {
			HttpResponse response = httpPostRequest(
					"/m/merchant/offer/redeem/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantRedeemOffer", responseStr);
			return gson.fromJson(responseStr, RedeemResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;

	}

	public static final String PAST_0 = "0";
	public static final String PAST_7 = "7";

	/**
	 * 
	 * @param period
	 *            PAST_0|PAST_7
	 * @return
	 */
	public PastResponse merchantPastOffer(String period) {
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpGetRequest("/m/merchant/offers/past/"
					+ period + "/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantPastOffer", responseStr);
			return gson.fromJson(responseStr, PastResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;

	}

	public SummaryResponse merchantSummary() {
		JSONObject obj = new JSONObject();
		try {
			HttpResponse response = httpGetRequest("/m/merchant/summary/", obj);
			String responseStr = EntityUtils.toString(response.getEntity());
			Log.d("merchantSummary", responseStr);
			return gson.fromJson(responseStr, SummaryResponse.class);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NullPointerException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}
}