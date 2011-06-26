//
//  SLTableItemCell.h
//  shoppleyMerchant
//
//  Created by yod on 6/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLTableItem.h"

@interface SLActiveOfferTableItemCell : TTTableMessageItemCell {
    
}

@end

@interface SLPastOfferTableItemCell : TTTableMessageItemCell {
    
}

@end

@interface SLRightValueTableItemCell : TTTableCaptionItemCell {
    
}

@end

@interface SLStarsTableItemCell : TTTableViewCell {
    SLStarsTableItem* _item;
}

@end

@interface SLRightStarsTableItemCell : TTTableTextItemCell {
    UIView* _starsView;
    CGFloat _starsViewWidth;
}

@end
