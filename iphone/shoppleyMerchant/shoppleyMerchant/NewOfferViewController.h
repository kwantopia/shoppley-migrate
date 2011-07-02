//
//  NewOfferViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLNewOffer.h"
#import "SLSelectAmountViewController.h"
#import "SLSelectDateViewController.h"

@interface NewOfferViewController : TTTableViewController <UITextFieldDelegate, UITextViewDelegate, SLSelectAmountDelegate, SLSelectDateDelegate> {
    SLNewOffer* _offer;
}

@property (nonatomic, retain) SLNewOffer* offer;

@property (nonatomic, retain) UITextField* titleField;
@property (nonatomic, retain) UITextView* descriptionField;
@property (nonatomic, retain) UITextField* durationField;

- (NSString*)selectStartTimeURL;
- (NSString*)selectAmountURL;

@end
