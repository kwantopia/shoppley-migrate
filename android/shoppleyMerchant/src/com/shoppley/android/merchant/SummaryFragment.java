package com.shoppley.android.merchant;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.github.droidfu.concurrent.BetterAsyncTask;
import com.github.droidfu.concurrent.BetterAsyncTaskCallable;
import com.shoppley.android.api.merchant.ShoppleyMerchantAPI;
import com.shoppley.android.api.merchant.SummaryResponse;

public class SummaryFragment extends Fragment {
	private TextView txtOffer;
	private TextView txtForwarded;
	private TextView txtReached;
	private TextView txtRedeemed;
	private Button btnRefresh;
	private LinearLayout layout;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		// TODO Auto-generated method stub
		super.onCreate(savedInstanceState);
	}

	private ShoppleyMerchantAPI api;
	private ProgressBar progress1;
	private ProgressBar progress2;
	private ProgressBar progress4;
	private ProgressBar progress3;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		MerchantApplication app = (MerchantApplication) getActivity()
				.getApplication();
		api = app.getAPI();
		View v = inflater.inflate(R.layout.summary, container, false);
		txtOffer = (TextView) v.findViewById(R.id.txtOffer);
		txtReached = (TextView) v.findViewById(R.id.txtReached);
		txtForwarded = (TextView) v.findViewById(R.id.txtForwarded);
		txtRedeemed = (TextView) v.findViewById(R.id.txtRedeemed);
		btnRefresh = (Button) v.findViewById(R.id.btnRefresh);
		progress1 = (ProgressBar) v.findViewById(R.id.progressBar1);
		progress2 = (ProgressBar) v.findViewById(R.id.progressBar2);
		progress3 = (ProgressBar) v.findViewById(R.id.progressBar3);
		progress4 = (ProgressBar) v.findViewById(R.id.progressBar4);
		layout = (LinearLayout) v.findViewById(R.id.linearLayoutSummary);

		btnRefresh.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				refresh();
			}
		});
		return v;
	}

	@Override
	public void onResume() {
		// TODO Auto-generated method stub
		super.onResume();
		refresh();

	}

	private void refresh() {
		setSummaryVisibility(false);

		BetterAsyncTask<Void, Void, SummaryResponse> task = new BetterAsyncTask<Void, Void, SummaryResponse>(
				getActivity()) {

			@Override
			protected void after(Context arg0, SummaryResponse arg1) {
				setSummaryVisibility(true);
				if (arg1 != null && arg1.result != null
						&& arg1.result.equals("1")) {
					txtOffer.setText(arg1.num_offers);
					txtReached.setText(arg1.total_received);
					txtForwarded.setText(arg1.total_forwarded);
					txtRedeemed.setText(arg1.total_redeemed);
				} else {
					setError();
					// if (arg1 == null) {

					// Utils.createDialog(getActivity(),
					// "An error occured. Please try again later").show();
					// } else {
					// Utils.createDialog(getActivity(), arg1.result_msg)
					// .show();
					// }
				}
			}

			@Override
			protected void handleError(Context arg0, Exception arg1) {
				setSummaryVisibility(true);
				// Utils.createDialog(getActivity(),
				// "An error occured. Please try again later").show();
				setError();
			}
		};
		task.setCallable(new BetterAsyncTaskCallable<Void, Void, SummaryResponse>() {

			public SummaryResponse call(
					BetterAsyncTask<Void, Void, SummaryResponse> arg0)
					throws Exception {

				return api.merchantSummary();
			}
		});
		task.execute();
	}

	protected void setSummaryVisibility(boolean visible) {
		if (visible) {
			progress1.setVisibility(View.GONE);
			progress2.setVisibility(View.GONE);
			progress3.setVisibility(View.GONE);
			progress4.setVisibility(View.GONE);
			txtOffer.setVisibility(View.VISIBLE);
			txtReached.setVisibility(View.VISIBLE);
			txtForwarded.setVisibility(View.VISIBLE);
			txtRedeemed.setVisibility(View.VISIBLE);
		} else {
			progress1.setVisibility(View.VISIBLE);
			progress2.setVisibility(View.VISIBLE);
			progress3.setVisibility(View.VISIBLE);
			progress4.setVisibility(View.VISIBLE);
			txtOffer.setVisibility(View.GONE);
			txtReached.setVisibility(View.GONE);
			txtForwarded.setVisibility(View.GONE);
			txtRedeemed.setVisibility(View.GONE);
		}
	}

	private void setError() {
		txtOffer.setText("Err");
		txtReached.setText("Err");
		txtForwarded.setText("Err");
		txtRedeemed.setText("Err");

	}
}
