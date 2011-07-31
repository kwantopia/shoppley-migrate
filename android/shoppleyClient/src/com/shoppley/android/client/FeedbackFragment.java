package com.shoppley.android.client;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.shoppley.android.api.customer.FeedbackOfferResponse;
import com.shoppley.android.api.customer.RedeemedOffer;
import com.shoppley.android.api.customer.ShoppleyCustomerAPI;
import com.shoppley.android.utils.Utils;

public class FeedbackFragment extends Fragment {

	private RedeemedOffer redeemedOffer;
	private View v;
	private Button btnSubmit;
	private TextView txtMerchantFeedback;
	private EditText edtTxtFeedback;

	public FeedbackFragment(RedeemedOffer redeemedOffer) {
		this.redeemedOffer = redeemedOffer;
	}

	@Override
	public void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		edtTxtFeedback.clearFocus();
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		v = inflater.inflate(R.layout.feedback, container, false);
		btnSubmit = (Button) v.findViewById(R.id.btnSubmit);
		txtMerchantFeedback = (TextView) v
				.findViewById(R.id.txtMerchantFeedback);
		edtTxtFeedback = (EditText) v.findViewById(R.id.edtTxtFeedback);
		txtMerchantFeedback.append(redeemedOffer.name + " from "
				+ redeemedOffer.merchant_name);
		btnSubmit.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				submitFeedback();
			}
		});
		edtTxtFeedback
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					public boolean onEditorAction(TextView v, int actionId,
							KeyEvent event) {
						if (actionId == EditorInfo.IME_ACTION_SEND) {
							// Validate
							submitFeedback();
							return true;
						}
						return false;
					}
				});
		return v;
	}

	protected void submitFeedback() {
		if (edtTxtFeedback.getText().toString().length() == 0) {
			Toast.makeText(getActivity(),
					"Please add feedback before submitting.", 500).show();
			return;
		}
		Utils.hideKeyboard(getActivity(), edtTxtFeedback.getWindowToken());
		ShoppleyApplication app = (ShoppleyApplication) getActivity()
				.getApplication();
		final ShoppleyCustomerAPI api = app.getAPI();

		final ProgressDialog loading = Utils.showLoading(getActivity(),
				"Submitting feedback...");
		BetterAsyncTask<Void, Void, FeedbackOfferResponse> task = new BetterAsyncTask<Void, Void, FeedbackOfferResponse>(
				getActivity()) {

			@Override
			protected void after(Context arg0, FeedbackOfferResponse arg1) {
				loading.hide();
				if (arg1 != null && arg1.result.equals("1")) {
					Toast.makeText(getActivity(), "Succesfully submitted.", 500)
							.show();
					FragmentManager fm = getFragmentManager();
					Utils.hideKeyboard(getActivity(),
							edtTxtFeedback.getWindowToken());
					fm.popBackStack();
				} else {
					Toast.makeText(getActivity(),
							"Unable to send feedback. Please try agian.", 500)
							.show();
				}
			}

			@Override
			protected void handleError(Context arg0, Exception arg1) {
				loading.hide();
				Toast.makeText(getActivity(),
						"Unable to send feedback. Please try agian.", 500)
						.show();
			}

		};
		task.setCallable(new BetterAsyncTaskCallable<Void, Void, FeedbackOfferResponse>() {

			public FeedbackOfferResponse call(
					BetterAsyncTask<Void, Void, FeedbackOfferResponse> arg0)
					throws Exception {
				return api.customerFeedbackOffer(edtTxtFeedback.getText()
						.toString(), redeemedOffer.offer_id);
			}
		});
		task.execute();
	}
}
