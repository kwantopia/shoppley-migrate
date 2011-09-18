package com.shoppley.android.merchant;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnCancelListener;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnFocusChangeListener;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.TextView.OnEditorActionListener;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.shoppley.android.api.merchant.RedeemResponse;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.utils.Utils;

public class RedeemFragment extends Fragment {
	private EditText edtPaid;
	private EditText edtCode;
	private Button btnRedeem;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		MerchantApplication app = (MerchantApplication) getActivity()
				.getApplication();
		final ShoppleyMerchantAPI api = app.getAPI();

		View v = inflater.inflate(R.layout.redeem, container, false);
		edtCode = (EditText) v.findViewById(R.id.edtCode);
		edtPaid = (EditText) v.findViewById(R.id.edtPaid);
		btnRedeem = (Button) v.findViewById(R.id.btnRedeem);
//		edtPaid.setOnFocusChangeListener(new OnFocusChangeListener() {
//			public void onFocusChange(View v, boolean hasFocus) {
//				if(!hasFocus){
//					Utils.hideKeyboard(getActivity(), edtPaid.getWindowToken());
//				}
//			}
//		});
//		edtCode.setOnFocusChangeListener(new OnFocusChangeListener() {
//			public void onFocusChange(View v, boolean hasFocus) {
//				if(!hasFocus){
//					Utils.hideKeyboard(getActivity(), edtPaid.getWindowToken());
//				}
//			}
//		});
		edtPaid.setOnEditorActionListener(new OnEditorActionListener() {

			public boolean onEditorAction(TextView v, int actionId,
					KeyEvent event) {
				if (actionId == EditorInfo.IME_ACTION_SEND) {
					edtPaid.clearFocus();
					Utils.hideKeyboard(getActivity(), edtPaid.getWindowToken());
					redeem();
					return true;
				} else {

					return false;
				}
			}

		});
		btnRedeem.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				Utils.hideKeyboard(getActivity(), edtPaid.getWindowToken());
				redeem();
			}
		});
		return v;
	}

	@Override
	public void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		edtCode.clearFocus();
	}

	@Override
	public void onPause() {
		// TODO Auto-generated method stub
		super.onPause();
	}

	private void redeem() {
		if (edtCode.getText().length() == 0 || edtPaid.getText().length() == 0) {
			Utils.createDialog(getActivity(),
					getResources().getString(R.string.offer_code_total_paid_cannot_be_blank)).show();
			return;
		}

		final ProgressDialog loading = Utils.showLoading(getActivity(),
				getResources().getString(R.string.redeeming));
		final BetterAsyncTask<Void, Void, RedeemResponse> task = new BetterAsyncTask<Void, Void, RedeemResponse>(
				getActivity()) {

			@Override
			protected void after(Context arg0, RedeemResponse arg1) {
				loading.hide();
				if (arg1 != null && arg1.result != null
						&& arg1.result.equals("1")) {
					Utils.createDialog(getActivity(), getResources().getString(R.string.successfully_redeemed))
							.show();
				} else {
					Utils.createDialog(getActivity(), arg1.result_msg).show();

				}
			}

			@Override
			protected void handleError(Context arg0, Exception arg1) {
				loading.hide();
				Utils.createDialog(getActivity(),
						getResources().getString(R.string.error_occured_please_try_again_later)).show();

			}
		};
		task.setCallable(new BetterAsyncTaskCallable<Void, Void, RedeemResponse>() {

			public RedeemResponse call(
					BetterAsyncTask<Void, Void, RedeemResponse> arg0)
					throws Exception {
				ShoppleyMerchantAPI api = ((MerchantApplication) getActivity()
						.getApplication()).getAPI();

				return api.merchantRedeemOffer(edtPaid.getText().toString(),
						edtCode.getText().toString());
			}
		});
		loading.setOnCancelListener(new OnCancelListener() {
			public void onCancel(DialogInterface arg0) {
				loading.hide();
				task.cancel(true);
			}
		});
		task.execute();
	}

}
