//
//  OfferDetailViewController.h
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLOffer.h"

@interface OfferDetailViewController : TTTableViewController {
    SLOffer* _offer;
}

@end

@interface OfferDetailHeaderView: UIView {
    SLOffer* _offer;
}

- (id)initWithFrame:(CGRect)frame offer:(SLOffer*)offer;

@end
