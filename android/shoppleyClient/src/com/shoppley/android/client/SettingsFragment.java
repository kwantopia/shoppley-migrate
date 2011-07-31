package com.shoppley.android.client;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import com.shoppley.android.api.customer.ShoppleyCustomerAPI;

public class SettingsFragment extends Fragment {
	@Override
	public void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
	}

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		ShoppleyApplication app = (ShoppleyApplication) getActivity()
				.getApplication();
		final ShoppleyCustomerAPI api = app.getAPI();

		View v = inflater.inflate(R.layout.settings, container, false);
		EditText edtTxtUsn = (EditText) v.findViewById(R.id.edtTxtUsn);
		edtTxtUsn.setText(api.getCustomerEmail());
		Button btnLgt = (Button) v.findViewById(R.id.btnLgt);
		btnLgt.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				// Do logout
				api.logout();
				getActivity().finish();
			}
		});
		return v;
	}
}
