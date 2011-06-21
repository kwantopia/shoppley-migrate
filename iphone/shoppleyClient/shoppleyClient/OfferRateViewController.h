//
//  OfferRateViewController.h
//  shoppleyClient
//
//  Created by yod on 6/20/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLRedeemedOffer.h"

@interface OfferRateViewController : TTTableViewController {
    SLRedeemedOffer* _offer;
    UIBarButtonItem* _doneButton;
    UIBarButtonItem* _cancelButton;
    
    NSNumber* _new_value;
}

@property (nonatomic, retain) NSNumber* new_value;

@end
