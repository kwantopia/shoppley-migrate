//
//  OfferFeedbackViewController.h
//  shoppleyClient
//
//  Created by yod on 6/19/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLRedeemedOffer.h"

@interface OfferFeedbackViewController : TTTableViewController {
    SLRedeemedOffer* _offer;
    UITextView* _commentTextView;
    UIBarButtonItem* _doneButton;
    UIBarButtonItem* _cancelButton;
}

@end
