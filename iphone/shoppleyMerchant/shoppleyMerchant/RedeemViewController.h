//
//  RedeemViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/29/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface RedeemViewController : TTTableViewController <UITextFieldDelegate> {
    UITextField* _offerCodeField;
    UITextField* _totalPaidField;
}

@property (nonatomic, retain) UITextField* offerCodeField;
@property (nonatomic, retain) UITextField* totalPaidField;

- (void)redeemClicked;

@end
