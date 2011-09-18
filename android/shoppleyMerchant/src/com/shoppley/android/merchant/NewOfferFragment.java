package com.shoppley.android.merchant;

import java.util.Date;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnCancelListener;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TimePicker;
import android.widget.Toast;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.shoppley.android.api.merchant.Offer;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.api.merchant.StartResponse;
import com.shoppley.android.utils.Utils;

public class NewOfferFragment extends Fragment {
	private Offer offer = null;
	private EditText edtTitle;
	private EditText edtDesc;
	private Spinner spinDate;
	private Spinner spinUnits;
	private TimePicker timePicker;
	private EditText edtAmount;
	private Button btnSubmit;
	private Spinner spinDuration;
	private DatePicker datePicker;
	private EditText edtDuration;

	/**
	 * Create a new instance of DetailsFragment, initialized to show the text at
	 * 'index'.
	 * 
	 * @param object
	 */

	public NewOfferFragment() {
		// TODO Auto-generated constructor stub
	}

	public NewOfferFragment(Offer offer) {
		this.offer = offer;
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

	}

	@Override
	public void onActivityCreated(Bundle savedInstanceState) {
		super.onActivityCreated(savedInstanceState);

	}

	@Override
	public void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		edtTitle.clearFocus();
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = inflater.inflate(R.layout.newoffer_detail, container, false);
		edtTitle = (EditText) v.findViewById(R.id.edtTitle);
		edtDesc = (EditText) v.findViewById(R.id.edtDesc);
		datePicker = (DatePicker) v.findViewById(R.id.datePicker);
		edtDuration = (EditText) v.findViewById(R.id.edtDuration);
		timePicker = (TimePicker) v.findViewById(R.id.timePicker);
		edtAmount = (EditText) v.findViewById(R.id.edtAmount);
		spinUnits = (Spinner) v.findViewById(R.id.spinUnits);
		btnSubmit = (Button) v.findViewById(R.id.btnSubmit);

		// String[] unitsItems = new String[] { "%", "$" };
		// ArrayAdapter<String> unitsAdapter = new ArrayAdapter<String>(
		// getActivity(), android.R.layout.simple_spinner_item, unitsItems);
		// unitsAdapter.setDropDownViewResource(R.layout.spin_dropdown);
		// spinUnits.setAdapter(unitsAdapter);
		// spinUnits.setSelection(1);

		// Fill in if offer is not null
		if (offer != null) {
			edtTitle.setText(offer.title);
			edtDesc.setText(offer.description);
			edtDuration.setText(offer.duration);
		}

		btnSubmit.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				if (edtTitle.getText().length() == 0
						|| edtDuration.getText().length() == 0) {
					Utils.createDialog(
							getActivity(),
							getString(R.string.title_description_cannot_be_blank))
							.show();
					return;
				}

				final ProgressDialog loading = Utils.showLoading(getActivity(),
						getString(R.string.submitting_new_offer));
				final BetterAsyncTask<Void, Void, StartResponse> task = new BetterAsyncTask<Void, Void, StartResponse>(
						getActivity()) {

					@Override
					protected void after(Context arg0, StartResponse arg1) {
						loading.hide();
						// TODO Auto-generated method stub
						if (arg1 != null && arg1.result != null
								&& arg1.result.equals("0")) {
							Toast.makeText(getActivity(),
									getString(R.string.successfully_submitted), 500)
									.show();
							FragmentManager fm = getFragmentManager();
							fm.popBackStack();
						} else {
							Utils.createDialog(
									getActivity(),
									getString(R.string.error_occured_please_try_again_later))
									.show();
						}
					}

					@Override
					protected void handleError(Context arg0, Exception arg1) {
						loading.hide();
						Utils.createDialog(
								getActivity(),
								getString(R.string.error_occured_please_try_again_later))
								.show();

					}
				};
				task.setCallable(new BetterAsyncTaskCallable<Void, Void, StartResponse>() {

					public StartResponse call(
							BetterAsyncTask<Void, Void, StartResponse> arg0)
							throws Exception {
						ShoppleyMerchantAPI api = ((MerchantApplication) getActivity()
								.getApplication()).getAPI();
						Date d = new Date();
						d.setMonth(datePicker.getMonth());
						d.setYear(datePicker.getYear());
						d.setDate(datePicker.getDayOfMonth());
						d.setHours(timePicker.getCurrentHour());
						d.setMinutes(timePicker.getCurrentMinute());

						return api.merchantStartOffer("0", d.getTime() + "",
								edtDesc.getText().toString(), edtDuration
										.getText().toString(), edtTitle
										.getText().toString(), "0");
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
		});

		return v;
	}
}
