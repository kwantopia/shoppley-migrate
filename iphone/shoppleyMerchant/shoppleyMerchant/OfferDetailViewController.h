//
//  OfferDetailViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLOffer.h"

@interface OfferDetailViewController : TTTableViewController {
    SLOffer* _offer;
    BOOL _isActiveOffer;
}

@end

@interface OfferDetailHeaderView: UIView {

}

- (id)initWithFrame:(CGRect)frame offer:(SLOffer*)offer;

@end
